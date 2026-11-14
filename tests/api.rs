//! The API against a real database; each test is named in PARITY.md. Run with `just test`.

mod common;

use axum::http::StatusCode;
use common::{Client, PASSWORD, app, pool, user};
use serde_json::{Value, json};

fn exercise_body(name: &str, sets: i32, variant: &str) -> Value {
    json!({ "name": name, "variant_name": variant, "sets": sets })
}

fn plan(date: &str, workout: Vec<Value>) -> Value {
    json!({ "date": date, "workout": workout })
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn anonymous_requests_are_refused() {
    let app = app(&pool().await).await;
    let anon = Client::anonymous(&app);
    for uri in [
        "/api/me",
        "/api/exercises",
        "/api/sessions",
        "/api/sessions/1",
        "/api/sessions/last-weight",
    ] {
        assert_eq!(anon.get(uri).await.0, StatusCode::UNAUTHORIZED, "{uri}");
    }
    assert_eq!(
        anon.call("POST", "/api/exercises", Some(json!({"name": "A"})))
            .await
            .0,
        StatusCode::UNAUTHORIZED
    );
    assert_eq!(anon.get("/api/healthz").await.0, StatusCode::OK);
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn login_logout_and_password_change() {
    let pool = pool().await;
    let app = app(&pool).await;
    let name = user(&pool, "pw").await;

    let mut wrong = Client::anonymous(&app);
    let (status, body) = wrong.try_login(&name, "not it").await;
    assert_eq!(
        (status, body["detail"].as_str()),
        (
            StatusCode::UNAUTHORIZED,
            Some("wrong user name or password")
        )
    );
    let (status, _) = wrong.try_login("nobody-at-all", PASSWORD).await;
    assert_eq!(
        status,
        StatusCode::UNAUTHORIZED,
        "unknown users fail the same way"
    );

    let me = Client::login(&app, &name.to_uppercase(), PASSWORD).await;
    let (_, body) = me.get("/api/me").await;
    assert_eq!(
        (body["username"].as_str(), body["dark_mode"].as_bool()),
        (Some(name.as_str()), Some(false))
    );

    let change = |current: &str, new: &str| json!({ "current": current, "new": new });
    let (status, body) = me
        .call(
            "POST",
            "/api/me/password",
            Some(change("not it", "a new password")),
        )
        .await;
    assert_eq!(
        (status, body["detail"].as_str()),
        (
            StatusCode::BAD_REQUEST,
            Some("Current password is incorrect.")
        )
    );
    assert_eq!(
        me.call("POST", "/api/me/password", Some(change(PASSWORD, "short")))
            .await
            .0,
        StatusCode::BAD_REQUEST
    );
    assert_eq!(
        me.call(
            "POST",
            "/api/me/password",
            Some(change(PASSWORD, "a new password"))
        )
        .await
        .0,
        StatusCode::NO_CONTENT
    );

    assert_eq!(
        me.call("POST", "/api/logout", None).await.0,
        StatusCode::NO_CONTENT
    );
    assert_eq!(me.get("/api/me").await.0, StatusCode::UNAUTHORIZED);
    assert_eq!(
        Client::anonymous(&app).try_login(&name, PASSWORD).await.0,
        StatusCode::UNAUTHORIZED
    );
    Client::login(&app, &name, "a new password").await;
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn login_is_throttled() {
    let pool = pool().await;
    let app = app(&pool).await;
    let name = user(&pool, "throttle").await;
    let mut client = Client::anonymous(&app);
    for _ in 0..5 {
        assert_eq!(
            client.try_login(&name, "not it").await.0,
            StatusCode::UNAUTHORIZED
        );
    }
    assert_eq!(
        client.try_login(&name, PASSWORD).await.0,
        StatusCode::TOO_MANY_REQUESTS
    );
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn legacy_scrypt_hash_logs_in_and_is_upgraded() {
    let pool = pool().await;
    let app = app(&pool).await;
    let name = user(&pool, "legacy").await;
    // Written by the Python version for "correct horse" (same vector as pi-common's tests).
    let legacy =
        "scrypt$16384$8$1$AAECAwQFBgcICQoLDA0ODw==$JbN2hANm9NOw4h5BRHZnbjzQ6Jr0QwNWojTOC2WgIbU=";
    sqlx::query!(
        "UPDATE users SET password_hash = $2 WHERE username = $1",
        name,
        legacy
    )
    .execute(&pool)
    .await
    .unwrap();
    Client::login(&app, &name, PASSWORD).await;
    let stored = sqlx::query_scalar!("SELECT password_hash FROM users WHERE username = $1", name)
        .fetch_one(&pool)
        .await
        .unwrap();
    assert!(stored.starts_with("$argon2id$"), "upgraded on login");
    Client::login(&app, &name, PASSWORD).await;
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn deleted_user_is_logged_out() {
    let pool = pool().await;
    let app = app(&pool).await;
    let name = user(&pool, "gone").await;
    let client = Client::login(&app, &name, PASSWORD).await;
    let id = fittracker::users::find_id(&pool, &name).await.unwrap();
    fittracker::users::delete(&pool, id).await.unwrap();
    assert_eq!(client.get("/api/me").await.0, StatusCode::UNAUTHORIZED);
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn preferences_are_per_user() {
    let pool = pool().await;
    let app = app(&pool).await;
    let (a, b) = (user(&pool, "pref-a").await, user(&pool, "pref-b").await);
    let (a, b) = (
        Client::login(&app, &a, PASSWORD).await,
        Client::login(&app, &b, PASSWORD).await,
    );
    let (status, prefs) = a
        .call(
            "PATCH",
            "/api/me/preferences",
            Some(json!({ "dark_mode": true })),
        )
        .await;
    assert_eq!(
        (status, prefs),
        (StatusCode::OK, json!({ "dark_mode": true }))
    );
    assert_eq!(a.get("/api/me").await.1["dark_mode"], true);
    assert_eq!(b.get("/api/me").await.1["dark_mode"], false);
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn users_cannot_touch_each_others_data() {
    let pool = pool().await;
    let app = app(&pool).await;
    let owner = Client::login(&app, &user(&pool, "owner").await, PASSWORD).await;
    let other = Client::login(&app, &user(&pool, "other").await, PASSWORD).await;
    let (_, ex) = owner
        .call("POST", "/api/exercises", Some(json!({ "name": "A" })))
        .await;
    let (_, s) = owner
        .call("POST", "/api/sessions", Some(plan("2026-11-01", vec![])))
        .await;
    for (kind, id) in [("exercises", &ex["id"]), ("sessions", &s["id"])] {
        let uri = format!("/api/{kind}/{id}");
        assert_eq!(other.get(&uri).await.0, StatusCode::NOT_FOUND, "{uri}");
        let body = if kind == "exercises" {
            json!({ "name": "B" })
        } else {
            plan("2026-11-02", vec![])
        };
        assert_eq!(
            other.call("PUT", &uri, Some(body)).await.0,
            StatusCode::NOT_FOUND,
            "{uri}"
        );
        assert_eq!(
            other.call("DELETE", &uri, None).await.0,
            StatusCode::NOT_FOUND,
            "{uri}"
        );
        assert_eq!(other.get(&format!("/api/{kind}")).await.1, json!([]));
        assert_eq!(
            owner.get(&uri).await.0,
            StatusCode::OK,
            "still there for its owner"
        );
    }
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn exercise_crud() {
    let pool = pool().await;
    let app = app(&pool).await;
    let me = Client::login(&app, &user(&pool, "lib").await, PASSWORD).await;
    assert_eq!(
        me.call("POST", "/api/exercises", Some(json!({ "name": " " })))
            .await
            .0,
        StatusCode::BAD_REQUEST
    );

    let body = json!({ "name": " B ", "label": "Dips", "variants": [{ "name": "1", "label": "Chairs" }, { "name": "", "label": "x" }] });
    let (status, b) = me.call("POST", "/api/exercises", Some(body)).await;
    assert_eq!(status, StatusCode::CREATED);
    assert_eq!(
        (b["name"].as_str(), b["variants"].as_array().unwrap().len()),
        (Some("B"), 1)
    );
    me.call(
        "POST",
        "/api/exercises",
        Some(json!({ "name": "A", "label": "Pushup" })),
    )
    .await;

    let (_, list) = me.get("/api/exercises").await;
    let names: Vec<&str> = list
        .as_array()
        .unwrap()
        .iter()
        .map(|e| e["name"].as_str().unwrap())
        .collect();
    assert_eq!(names, ["A", "B"], "sorted by name");

    let uri = format!("/api/exercises/{}", b["id"]);
    let renamed =
        json!({ "name": "B", "label": "Dips", "variants": [{ "name": "2", "label": "Bars" }] });
    let (status, updated) = me.call("PUT", &uri, Some(renamed)).await;
    assert_eq!(
        (status, updated["variants"][0]["name"].as_str()),
        (StatusCode::OK, Some("2"))
    );
    assert_eq!(
        me.call("DELETE", &uri, None).await.0,
        StatusCode::NO_CONTENT
    );
    assert_eq!(me.get(&uri).await.0, StatusCode::NOT_FOUND);
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn session_crud() {
    let pool = pool().await;
    let app = app(&pool).await;
    let me = Client::login(&app, &user(&pool, "sessions").await, PASSWORD).await;
    let (status, older) = me
        .call(
            "POST",
            "/api/sessions",
            Some(plan("2026-11-01", vec![exercise_body("A", 3, "1")])),
        )
        .await;
    assert_eq!(
        (status, older["completed"].as_bool()),
        (StatusCode::CREATED, Some(false))
    );
    let (_, newer) = me
        .call("POST", "/api/sessions", Some(plan("2026-11-08", vec![])))
        .await;

    let (_, list) = me.get("/api/sessions").await;
    let dates: Vec<&str> = list
        .as_array()
        .unwrap()
        .iter()
        .map(|s| s["date"].as_str().unwrap())
        .collect();
    assert_eq!(dates, ["2026-11-08", "2026-11-01"], "newest first");
    let ex = &list[1]["workout"][0];
    assert_eq!(
        (ex["reps"].as_i64(), ex["rest_seconds"].as_i64()),
        (Some(10), Some(90)),
        "Python defaults"
    );

    let uri = format!("/api/sessions/{}", older["id"]);
    let mut reflected = older.clone();
    reflected.as_object_mut().unwrap().remove("id");
    reflected["completed"] = json!(true);
    reflected["energy_level"] = json!(4);
    reflected["weight"] = json!(72.5);
    reflected["notes"] = json!("  good  ");
    let (status, saved) = me.call("PUT", &uri, Some(reflected)).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(
        (saved["notes"].as_str(), saved["energy_level"].as_i64()),
        (Some("good"), Some(4))
    );

    let no_date = json!({ "date": "", "workout": [] });
    assert_eq!(
        me.call("PUT", &uri, Some(no_date)).await.0,
        StatusCode::BAD_REQUEST
    );
    assert_eq!(
        me.call("DELETE", &format!("/api/sessions/{}", newer["id"]), None)
            .await
            .0,
        StatusCode::NO_CONTENT
    );
    assert_eq!(me.get("/api/sessions").await.1.as_array().unwrap().len(), 1);
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn session_validation() {
    let pool = pool().await;
    let app = app(&pool).await;
    let me = Client::login(&app, &user(&pool, "rules").await, PASSWORD).await;
    let both = json!({ "name": "A", "reps": 10, "duration": 30 });
    let (status, body) = me
        .call(
            "POST",
            "/api/sessions",
            Some(plan("2026-11-01", vec![both])),
        )
        .await;
    assert_eq!(status, StatusCode::BAD_REQUEST);
    assert!(
        body["detail"]
            .as_str()
            .unwrap()
            .contains("reps or duration")
    );
    let too_many = json!({ "name": "A", "sets": 101 });
    assert_eq!(
        me.call(
            "POST",
            "/api/sessions",
            Some(plan("2026-11-01", vec![too_many]))
        )
        .await
        .0,
        StatusCode::BAD_REQUEST
    );
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn last_used_effort() {
    let pool = pool().await;
    let app = app(&pool).await;
    let me = Client::login(&app, &user(&pool, "last").await, PASSWORD).await;
    let other = Client::login(&app, &user(&pool, "nosy").await, PASSWORD).await;
    me.call(
        "POST",
        "/api/sessions",
        Some(plan("2026-11-01", vec![exercise_body("A", 3, "1")])),
    )
    .await;
    me.call(
        "POST",
        "/api/sessions",
        Some(plan("2026-11-08", vec![exercise_body("A", 5, "2")])),
    )
    .await;
    assert_eq!(
        me.get("/api/sessions/last-used?name=A&variant=1").await.1["sets"],
        3
    );
    assert_eq!(
        me.get("/api/sessions/last-used?name=A&variant=9").await.1["sets"],
        5
    );
    assert_eq!(
        me.get("/api/sessions/last-used?name=Z").await.1,
        Value::Null
    );
    assert_eq!(
        other.get("/api/sessions/last-used?name=A").await.1,
        Value::Null,
        "never another user's"
    );
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn last_weight() {
    let pool = pool().await;
    let app = app(&pool).await;
    let me = Client::login(&app, &user(&pool, "weight").await, PASSWORD).await;
    assert_eq!(me.get("/api/sessions/last-weight").await.1, Value::Null);
    let done = json!({ "date": "2026-11-01", "completed": true, "weight": 71.2 });
    me.call("POST", "/api/sessions", Some(done)).await;
    me.call(
        "POST",
        "/api/sessions",
        Some(json!({ "date": "2026-11-09", "weight": 99 })),
    )
    .await;
    assert_eq!(me.get("/api/sessions/last-weight").await.1, json!(71.2));
}
