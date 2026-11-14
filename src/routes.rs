//! HTTP routes: the JSON API under `/api`, and the embedded Svelte app for everything else.
//!
//! | Route | Does |
//! | --- | --- |
//! | `POST /api/login`, `POST /api/logout`, `GET /api/me` | session (pi-common auth) |
//! | `POST /api/me/password`, `PATCH /api/me/preferences` | account menu, theme toggle |
//! | `GET, POST /api/exercises`, `GET, PUT, DELETE /api/exercises/{id}` | exercise library |
//! | `GET, POST /api/sessions`, `GET, PUT, DELETE /api/sessions/{id}` | sessions (newest first) |
//! | `GET /api/sessions/last-used?name=&variant=` | effort pre-fill for a new row |
//! | `GET /api/sessions/last-weight` | weight pre-fill for the reflection |

use std::sync::Arc;
use std::time::Duration;

use axum::extract::{FromRef, Path, Query, State};
use axum::http::StatusCode;
use axum::routing::{get, patch, post};
use axum::{Json, Router};
use axum_extra::extract::cookie::CookieJar;
use pi_common::auth::{self, LoginThrottle, Session as Login, SessionOptions, Sessions};
use pi_common::cli::{Context, MIN_PASSWORD_LEN};
use pi_common::{ApiResult, AppError, BoxError, static_files};
use rust_embed::RustEmbed;
use serde::{Deserialize, Serialize};
use sqlx::PgPool;

use crate::docs::{self, DocKind, Stored};
use crate::model::{self, Exercise, Session, SessionExercise};
use crate::users::{self, Preferences, Users};

/// The Svelte build (`web/dist`), embedded at compile time; read from disk in debug builds.
#[derive(RustEmbed)]
#[folder = "web/dist"]
#[allow_missing = true]
struct Assets;

/// Failed logins allowed per user name in [`THROTTLE_WINDOW`] (the Python version's limits).
const THROTTLE_FAILURES: usize = 5;
const THROTTLE_WINDOW: Duration = Duration::from_secs(5 * 60);

/// Shared state of the handlers.
#[derive(Clone, FromRef)]
pub struct AppState {
    pool: PgPool,
    sessions: Sessions,
    throttle: Arc<LoginThrottle>,
}

/// Build the router; called by `serve` with the database ready.
pub async fn build(ctx: Context) -> Result<Router, BoxError> {
    let sessions = Sessions::new(
        ctx.pool.clone(),
        SessionOptions {
            table: "auth_sessions",
            cookie_name: "fittracker_session",
            days: ctx.config.session_days,
            secure: ctx.config.cookie_secure,
        },
    );
    sessions.purge_expired().await?;
    let state = AppState {
        pool: ctx.pool,
        sessions,
        throttle: Arc::new(LoginThrottle::new(THROTTLE_FAILURES, THROTTLE_WINDOW)),
    };
    let session_routes = doc_routes::<Session>()
        .route("/last-used", get(last_used))
        .route("/last-weight", get(last_weight));
    Ok(Router::new()
        .route("/api/login", post(login))
        .route("/api/logout", post(logout))
        .route("/api/me", get(me))
        .route("/api/me/password", post(change_password))
        .route("/api/me/preferences", patch(set_preferences))
        .nest("/api/exercises", doc_routes::<Exercise>())
        .nest("/api/sessions", session_routes)
        .with_state(state)
        .merge(static_files::router::<Assets, ()>()))
}

// ---- account ----

#[derive(Deserialize)]
struct LoginBody {
    username: String,
    password: String,
}

/// The logged-in user, the CSRF token the client must send back, and the theme.
#[derive(Serialize)]
struct Me {
    username: String,
    csrf_token: String,
    dark_mode: bool,
}

async fn me_for(pool: &PgPool, login: &Login) -> ApiResult<Json<Me>> {
    let user = users::get(pool, login.user_id).await?;
    Ok(Json(Me {
        username: user.username,
        csrf_token: login.csrf_token.clone(),
        dark_mode: user.preferences.dark_mode,
    }))
}

async fn login(
    State(state): State<AppState>,
    jar: CookieJar,
    Json(body): Json<LoginBody>,
) -> ApiResult<(CookieJar, Json<Me>)> {
    let user_id = auth::verify_login(
        &Users(&state.pool),
        &state.throttle,
        &body.username,
        &body.password,
    )
    .await?;
    let (jar, session) = state.sessions.start(jar, user_id).await?;
    Ok((jar, me_for(&state.pool, &session).await?))
}

async fn me(State(pool): State<PgPool>, login: Login) -> ApiResult<Json<Me>> {
    me_for(&pool, &login).await
}

async fn logout(
    State(sessions): State<Sessions>,
    jar: CookieJar,
    login: Login,
) -> ApiResult<(CookieJar, StatusCode)> {
    Ok((sessions.end(jar, &login).await?, StatusCode::NO_CONTENT))
}

#[derive(Deserialize)]
struct PasswordBody {
    current: String,
    new: String,
}

/// Change one's own password: the current one is checked (and throttled) like a login.
async fn change_password(
    State(state): State<AppState>,
    login: Login,
    Json(body): Json<PasswordBody>,
) -> ApiResult<StatusCode> {
    if body.new.chars().count() < MIN_PASSWORD_LEN {
        return Err(AppError::BadRequest(format!(
            "Password must be at least {MIN_PASSWORD_LEN} characters."
        )));
    }
    let username = users::get(&state.pool, login.user_id).await?.username;
    let checked = auth::verify_login(
        &Users(&state.pool),
        &state.throttle,
        &username,
        &body.current,
    )
    .await;
    match checked {
        Ok(_) => {}
        // A 401 would look like a lost session to the client.
        Err(AppError::InvalidCredentials) => {
            return Err(AppError::BadRequest(
                "Current password is incorrect.".into(),
            ));
        }
        Err(other) => return Err(other),
    }
    users::set_password(&state.pool, login.user_id, &body.new).await?;
    Ok(StatusCode::NO_CONTENT)
}

async fn set_preferences(
    State(pool): State<PgPool>,
    login: Login,
    Json(changes): Json<Preferences>,
) -> ApiResult<Json<Preferences>> {
    Ok(Json(
        users::update_preferences(&pool, login.user_id, changes).await?,
    ))
}

// ---- documents (exercises and sessions) ----

fn doc_routes<T: DocKind>() -> Router<AppState> {
    Router::new()
        .route("/", get(list_docs::<T>).post(create_doc::<T>))
        .route(
            "/{id}",
            get(get_doc::<T>)
                .put(update_doc::<T>)
                .delete(delete_doc::<T>),
        )
}

async fn list_docs<T: DocKind>(
    State(pool): State<PgPool>,
    login: Login,
) -> ApiResult<Json<Vec<Stored<T>>>> {
    Ok(Json(docs::list(&pool, users::to_id(login.user_id)?).await?))
}

async fn get_doc<T: DocKind>(
    State(pool): State<PgPool>,
    login: Login,
    Path(id): Path<i32>,
) -> ApiResult<Json<Stored<T>>> {
    Ok(Json(
        docs::get(&pool, users::to_id(login.user_id)?, id).await?,
    ))
}

async fn create_doc<T: DocKind>(
    State(pool): State<PgPool>,
    login: Login,
    Json(doc): Json<T>,
) -> ApiResult<(StatusCode, Json<Stored<T>>)> {
    let doc = doc.validate().map_err(AppError::BadRequest)?;
    let stored = docs::insert(&pool, users::to_id(login.user_id)?, doc).await?;
    Ok((StatusCode::CREATED, Json(stored)))
}

async fn update_doc<T: DocKind>(
    State(pool): State<PgPool>,
    login: Login,
    Path(id): Path<i32>,
    Json(doc): Json<T>,
) -> ApiResult<Json<Stored<T>>> {
    let doc = doc.validate().map_err(AppError::BadRequest)?;
    Ok(Json(
        docs::update(&pool, users::to_id(login.user_id)?, id, doc).await?,
    ))
}

async fn delete_doc<T: DocKind>(
    State(pool): State<PgPool>,
    login: Login,
    Path(id): Path<i32>,
) -> ApiResult<StatusCode> {
    docs::delete::<T>(&pool, users::to_id(login.user_id)?, id).await?;
    Ok(StatusCode::NO_CONTENT)
}

// ---- pre-fills ----

#[derive(Deserialize)]
struct LastUsedQuery {
    name: String,
    #[serde(default)]
    variant: String,
}

async fn last_used(
    State(pool): State<PgPool>,
    login: Login,
    Query(q): Query<LastUsedQuery>,
) -> ApiResult<Json<Option<SessionExercise>>> {
    let sessions = docs::list::<Session>(&pool, users::to_id(login.user_id)?).await?;
    let found = model::last_used(sessions.iter().map(|s| &s.doc), &q.name, &q.variant);
    Ok(Json(found.cloned()))
}

async fn last_weight(State(pool): State<PgPool>, login: Login) -> ApiResult<Json<Option<f64>>> {
    let sessions = docs::list::<Session>(&pool, users::to_id(login.user_id)?).await?;
    Ok(Json(model::last_weight(sessions.iter().map(|s| &s.doc))))
}
