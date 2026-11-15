//! Storage of the per-user JSON documents (`exercises`, `sessions`): one generic implementation for both,
//! as both tables have the same shape (`id`, `doc`, `user_id`).
//!
//! These queries are plain `sqlx::query` (the table name varies), so the integration tests are what checks
//! them; everything else uses compile-time checked `query!`.

use pi_common::AppError;
use serde::Serialize;
use serde::de::DeserializeOwned;
use sqlx::types::Json;
use sqlx::{AssertSqlSafe, PgPool};

use crate::model::{self, Exercise, Session};

/// A kind of document and its table.
pub trait DocKind: Serialize + DeserializeOwned + Send + Sync + Unpin + 'static {
    /// Table name (a constant, never user input).
    const TABLE: &'static str;
    /// `ORDER BY` of [`list`].
    const ORDER: &'static str;
    /// Clean up and check a document from a client.
    fn validate(self) -> Result<Self, String>;
}

impl DocKind for Exercise {
    const TABLE: &'static str = "exercises";
    const ORDER: &'static str = "doc ->> 'name', id";
    fn validate(self) -> Result<Self, String> {
        model::validate::exercise(self)
    }
}

impl DocKind for Session {
    const TABLE: &'static str = "sessions";
    const ORDER: &'static str = "doc ->> 'date' DESC, id DESC";
    fn validate(self) -> Result<Self, String> {
        model::validate::session(self)
    }
}

/// A document with its row id, as the API returns it: `{"id": 1, ...fields}`.
#[derive(Debug, Clone, Serialize)]
pub struct Stored<T> {
    pub id: i32,
    #[serde(flatten)]
    pub doc: T,
}

type Row<T> = (i32, Json<T>);

fn stored<T>((id, Json(doc)): Row<T>) -> Stored<T> {
    Stored { id, doc }
}

/// All of a user's documents, in the kind's order.
pub async fn list<T: DocKind>(pool: &PgPool, user_id: i32) -> Result<Vec<Stored<T>>, AppError> {
    let sql = format!(
        "SELECT id, doc FROM {} WHERE user_id = $1 ORDER BY {}",
        T::TABLE,
        T::ORDER
    );
    let rows: Vec<Row<T>> = sqlx::query_as(AssertSqlSafe(sql))
        .bind(user_id)
        .fetch_all(pool)
        .await?;
    Ok(rows.into_iter().map(stored).collect())
}

/// One of the user's documents; 404 if it does not exist or belongs to someone else.
pub async fn get<T: DocKind>(pool: &PgPool, user_id: i32, id: i32) -> Result<Stored<T>, AppError> {
    let sql = format!(
        "SELECT id, doc FROM {} WHERE id = $1 AND user_id = $2",
        T::TABLE
    );
    let row: Row<T> = sqlx::query_as(AssertSqlSafe(sql))
        .bind(id)
        .bind(user_id)
        .fetch_one(pool)
        .await?;
    Ok(stored(row))
}

pub async fn insert<T: DocKind>(
    pool: &PgPool,
    user_id: i32,
    doc: T,
) -> Result<Stored<T>, AppError> {
    let sql = format!(
        "INSERT INTO {} (doc, user_id) VALUES ($1, $2) RETURNING id, doc",
        T::TABLE
    );
    let row: Row<T> = sqlx::query_as(AssertSqlSafe(sql))
        .bind(Json(doc))
        .bind(user_id)
        .fetch_one(pool)
        .await?;
    Ok(stored(row))
}

/// Replace one of the user's documents; 404 if it does not exist or belongs to someone else.
pub async fn update<T: DocKind>(
    pool: &PgPool,
    user_id: i32,
    id: i32,
    doc: T,
) -> Result<Stored<T>, AppError> {
    let sql = format!(
        "UPDATE {} SET doc = $1 WHERE id = $2 AND user_id = $3 RETURNING id, doc",
        T::TABLE
    );
    let row: Row<T> = sqlx::query_as(AssertSqlSafe(sql))
        .bind(Json(doc))
        .bind(id)
        .bind(user_id)
        .fetch_one(pool)
        .await?;
    Ok(stored(row))
}

/// Delete one of the user's documents; 404 if it does not exist or belongs to someone else.
pub async fn delete<T: DocKind>(pool: &PgPool, user_id: i32, id: i32) -> Result<(), AppError> {
    let sql = format!("DELETE FROM {} WHERE id = $1 AND user_id = $2", T::TABLE);
    let done = sqlx::query(AssertSqlSafe(sql))
        .bind(id)
        .bind(user_id)
        .execute(pool)
        .await?;
    if done.rows_affected() == 0 {
        return Err(AppError::NotFound);
    }
    Ok(())
}
