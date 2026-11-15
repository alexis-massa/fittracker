//! Shared helpers for the integration tests: a database, the real router, and a client that logs in and
//! sends the session cookie and CSRF token like the browser does. Run with `just test`.
#![allow(dead_code)] // each test binary uses a different subset

use axum::Router;
use axum::body::Body;
use axum::http::{Request, StatusCode, header};
use http_body_util::BodyExt;
use pi_common::cli::Context;
use pi_common::config::Config;
use serde_json::{Value, json};
use sqlx::PgPool;
use tower::ServiceExt;

pub const PASSWORD: &str = "correct horse";

/// The test database (recreated by `just test`), migrated.
pub async fn pool() -> PgPool {
    let url = test_url();
    let pool = pi_common::db::connect(&url).await.unwrap();
    pi_common::db::migrate(&pool, fittracker::migrator())
        .await
        .unwrap();
    pool
}

pub fn test_url() -> String {
    std::env::var("TEST_DATABASE_URL").expect("TEST_DATABASE_URL (run `just test`)")
}

/// The app's router with the shared middleware, as `serve` builds it.
pub async fn app(pool: &PgPool) -> Router {
    let config = Config {
        database_url: test_url(),
        app_domain: "app.test".into(),
        bind_addr: "127.0.0.1:0".parse().unwrap(),
        cookie_secure: true,
        session_days: 1,
    };
    let ctx = Context {
        config,
        pool: pool.clone(),
    };
    let router = fittracker::routes::build(ctx).await.unwrap();
    pi_common::server::wrap(router, pool.clone(), Default::default())
}

/// A user with a unique name (tests share one database and run in parallel).
pub async fn user(pool: &PgPool, name: &str) -> String {
    let unique = format!("{name}-{}", rand_suffix());
    fittracker::users::create(pool, &unique, PASSWORD)
        .await
        .unwrap();
    unique
}

fn rand_suffix() -> String {
    use std::sync::atomic::{AtomicU32, Ordering};
    static NEXT: AtomicU32 = AtomicU32::new(0);
    format!(
        "{}{}",
        std::process::id(),
        NEXT.fetch_add(1, Ordering::Relaxed)
    )
}

/// A browser: keeps the session cookie and the CSRF token.
pub struct Client {
    app: Router,
    cookie: Option<String>,
    csrf: Option<String>,
}

impl Client {
    pub fn anonymous(app: &Router) -> Self {
        Self {
            app: app.clone(),
            cookie: None,
            csrf: None,
        }
    }

    /// Log in, panicking on failure.
    pub async fn login(app: &Router, username: &str, password: &str) -> Self {
        let mut client = Self::anonymous(app);
        let (status, _) = client.try_login(username, password).await;
        assert_eq!(status, StatusCode::OK, "login of {username}");
        client
    }

    /// Attempt a login; on success the client keeps the session.
    pub async fn try_login(&mut self, username: &str, password: &str) -> (StatusCode, Value) {
        let body = json!({ "username": username, "password": password });
        let (status, cookie, json) = self.send("POST", "/api/login", Some(body)).await;
        if status == StatusCode::OK {
            self.cookie = cookie;
            self.csrf = json["csrf_token"].as_str().map(str::to_owned);
        }
        (status, json)
    }

    pub async fn get(&self, uri: &str) -> (StatusCode, Value) {
        self.call("GET", uri, None).await
    }

    pub async fn call(&self, method: &str, uri: &str, body: Option<Value>) -> (StatusCode, Value) {
        let (status, _, json) = self.send(method, uri, body).await;
        (status, json)
    }

    async fn send(
        &self,
        method: &str,
        uri: &str,
        body: Option<Value>,
    ) -> (StatusCode, Option<String>, Value) {
        let mut req = Request::builder()
            .method(method)
            .uri(uri)
            .header(header::HOST, "app.test");
        if let Some(cookie) = &self.cookie {
            req = req.header(header::COOKIE, cookie);
        }
        if let Some(csrf) = &self.csrf {
            req = req.header("x-csrf-token", csrf);
        }
        let req = match body {
            Some(b) => req
                .header(header::CONTENT_TYPE, "application/json")
                .body(Body::from(b.to_string())),
            None => req.body(Body::empty()),
        };
        let res = self.app.clone().oneshot(req.unwrap()).await.unwrap();
        let status = res.status();
        let cookie = res
            .headers()
            .get(header::SET_COOKIE)
            .map(|v| v.to_str().unwrap().split(';').next().unwrap().to_owned());
        let bytes = res.into_body().collect().await.unwrap().to_bytes();
        (
            status,
            cookie,
            serde_json::from_slice(&bytes).unwrap_or(Value::Null),
        )
    }
}
