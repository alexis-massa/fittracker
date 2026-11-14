//! Users, their passwords and preferences.

use std::sync::LazyLock;

use pi_common::AppError;
use pi_common::auth::{self, Credentials, PasswordStore};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use sqlx::types::Json;

/// Per-user settings, stored in `users.preferences` (unknown keys are kept as they are).
#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct Preferences {
    pub dark_mode: bool,
}

/// A user as the app shows it.
#[derive(Debug, Clone, Serialize)]
pub struct User {
    pub id: i32,
    pub username: String,
    pub preferences: Preferences,
}

/// One line of `list-users`.
#[derive(Debug)]
pub struct Summary {
    pub username: String,
    pub sessions: i64,
    pub exercises: i64,
}

/// User names are 3–32 letters, digits, `.`, `_` or `-` (as in the Python version).
pub fn validate_username(raw: &str) -> Result<String, AppError> {
    static PATTERN: LazyLock<regex_lite::Regex> =
        LazyLock::new(|| regex_lite::Regex::new(r"^[A-Za-z0-9_.-]{3,32}$").expect("valid regex"));
    let name = raw.trim();
    if PATTERN.is_match(name) {
        Ok(name.to_owned())
    } else {
        Err(AppError::BadRequest(
            "Username must be 3-32 characters: letters, digits, '.', '_' or '-'.".into(),
        ))
    }
}

/// The `users` table, as seen by [`auth::verify_login`].
pub struct Users<'a>(pub &'a PgPool);

impl PasswordStore for Users<'_> {
    async fn credentials(&self, username: &str) -> Result<Option<Credentials>, AppError> {
        let row = sqlx::query!(
            "SELECT id, password_hash FROM users WHERE lower(username) = lower($1)",
            username.trim()
        )
        .fetch_optional(self.0)
        .await?;
        Ok(row.map(|r| Credentials {
            user_id: r.id.into(),
            password_hash: r.password_hash,
        }))
    }

    async fn set_password_hash(&self, user_id: i64, hash: &str) -> Result<(), AppError> {
        sqlx::query!(
            "UPDATE users SET password_hash = $2 WHERE id = $1",
            to_id(user_id)?,
            hash
        )
        .execute(self.0)
        .await?;
        Ok(())
    }
}

/// Row ids are `integer` in this schema; session user ids are `i64` in pi-common.
pub fn to_id(user_id: i64) -> Result<i32, AppError> {
    i32::try_from(user_id).map_err(|_| AppError::NotFound)
}

pub async fn get(pool: &PgPool, user_id: i64) -> Result<User, AppError> {
    let row = sqlx::query!(
        r#"SELECT id, username, preferences AS "preferences: Json<Preferences>" FROM users WHERE id = $1"#,
        to_id(user_id)?
    )
    .fetch_one(pool)
    .await?;
    Ok(User {
        id: row.id,
        username: row.username,
        preferences: row.preferences.0,
    })
}

pub async fn find_id(pool: &PgPool, username: &str) -> Result<i32, AppError> {
    sqlx::query_scalar!(
        "SELECT id FROM users WHERE lower(username) = lower($1)",
        username.trim()
    )
    .fetch_optional(pool)
    .await?
    .ok_or_else(|| AppError::BadRequest(format!("No such user: {username}")))
}

/// Create a user and return its id.
pub async fn create(pool: &PgPool, username: &str, password: &str) -> Result<i32, AppError> {
    let username = validate_username(username)?;
    let hash = auth::hash_password(password).await?;
    sqlx::query_scalar!(
        "INSERT INTO users (username, password_hash) VALUES ($1, $2) RETURNING id",
        username,
        hash
    )
    .fetch_one(pool)
    .await
    .map_err(|e| match &e {
        sqlx::Error::Database(db) if db.is_unique_violation() => {
            AppError::Conflict(format!("Username '{username}' is already taken."))
        }
        _ => e.into(),
    })
}

/// Replace a user's password (the caller decides which sessions to end).
pub async fn set_password(pool: &PgPool, user_id: i64, password: &str) -> Result<(), AppError> {
    Users(pool)
        .set_password_hash(user_id, &auth::hash_password(password).await?)
        .await
}

/// Merge `changes` into the stored preferences and return the result.
pub async fn update_preferences(
    pool: &PgPool,
    user_id: i64,
    changes: Preferences,
) -> Result<Preferences, AppError> {
    let row = sqlx::query_scalar!(
        r#"UPDATE users SET preferences = preferences || $2 WHERE id = $1
           RETURNING preferences AS "preferences: Json<Preferences>""#,
        to_id(user_id)?,
        Json(changes) as _
    )
    .fetch_one(pool)
    .await?;
    Ok(row.0)
}

/// Every user with how much they have, oldest first.
pub async fn summaries(pool: &PgPool) -> Result<Vec<Summary>, AppError> {
    let rows = sqlx::query_as!(
        Summary,
        r#"SELECT u.username,
                  (SELECT count(*) FROM sessions s WHERE s.user_id = u.id) AS "sessions!",
                  (SELECT count(*) FROM exercises e WHERE e.user_id = u.id) AS "exercises!"
           FROM users u ORDER BY u.id"#
    )
    .fetch_all(pool)
    .await?;
    Ok(rows)
}

/// Delete a user; their sessions and exercises go with them (ON DELETE CASCADE).
pub async fn delete(pool: &PgPool, user_id: i32) -> Result<(), AppError> {
    sqlx::query!("DELETE FROM users WHERE id = $1", user_id)
        .execute(pool)
        .await?;
    Ok(())
}

/// Rows from before multi-user support, which belong to nobody.
pub async fn count_unowned(pool: &PgPool) -> Result<i64, AppError> {
    let n = sqlx::query_scalar!(
        r#"SELECT (SELECT count(*) FROM sessions WHERE user_id IS NULL)
                + (SELECT count(*) FROM exercises WHERE user_id IS NULL) AS "n!""#
    )
    .fetch_one(pool)
    .await?;
    Ok(n)
}

/// Give every unowned row to a user; returns how many rows changed.
pub async fn claim_unowned(pool: &PgPool, user_id: i32) -> Result<u64, AppError> {
    let mut tx = pool.begin().await?;
    let sessions = sqlx::query!(
        "UPDATE sessions SET user_id = $1 WHERE user_id IS NULL",
        user_id
    )
    .execute(&mut *tx)
    .await?;
    let exercises = sqlx::query!(
        "UPDATE exercises SET user_id = $1 WHERE user_id IS NULL",
        user_id
    )
    .execute(&mut *tx)
    .await?;
    tx.commit().await?;
    Ok(sessions.rows_affected() + exercises.rows_affected())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn usernames_follow_the_python_rule() {
        assert_eq!(validate_username(" ann.b-c_1 ").unwrap(), "ann.b-c_1");
        for bad in ["ab", "has space", "é", &"x".repeat(33)] {
            assert!(validate_username(bad).is_err(), "{bad}");
        }
    }
}
