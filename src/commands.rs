//! The app's own subcommands (next to pi-common's `serve`, `migrate`, `healthcheck`, `baseline`).
//! They replace the Python `scripts/manage_users.py` and `scripts/seed_exercises.py`.

use std::io::BufRead;

use clap::Subcommand;
use pi_common::cli::{self, Context};
use pi_common::{AppError, BoxError};

use crate::docs;
use crate::model::Exercise;
use crate::users;

/// The Lafay exercise library offered to new users.
const LAFAY_EXERCISES: &str = include_str!("../data/lafay_exercises.json");

#[derive(Debug, Subcommand)]
pub enum Command {
    /// Create a user; asks for the password (or reads one line from stdin).
    CreateUser { username: String },
    /// Change a user's password and log them out everywhere.
    SetPassword { username: String },
    /// List users with their number of sessions and exercises.
    ListUsers,
    /// Delete a user and all their data; asks you to type the user name.
    DeleteUser { username: String },
    /// Give rows from before multi-user support (no owner) to a user.
    ClaimLegacy { username: String },
    /// Add the Lafay exercise library to a user's exercises (skips names they already have).
    SeedExercises { username: String },
}

impl Command {
    pub async fn run(self, ctx: Context) -> Result<(), BoxError> {
        let pool = &ctx.pool;
        match self {
            Self::CreateUser { username } => {
                let id = users::create(pool, &username, &cli::read_new_password()?).await?;
                println!("Created user '{username}' (id {id}).");
                println!(
                    "Optionally give them the Lafay exercise library: seed-exercises {username}"
                );
            }
            Self::SetPassword { username } => {
                let id = users::find_id(pool, &username).await?;
                users::set_password(pool, id.into(), &cli::read_new_password()?).await?;
                sqlx::query!("DELETE FROM auth_sessions WHERE user_id = $1", id)
                    .execute(pool)
                    .await?;
                println!("Password updated for '{username}'; their sessions were ended.");
            }
            Self::ListUsers => {
                let all = users::summaries(pool).await?;
                for u in &all {
                    println!(
                        "{:<20} {} sessions, {} exercises",
                        u.username, u.sessions, u.exercises
                    );
                }
                if all.is_empty() {
                    println!("No users yet.");
                }
                let unowned = users::count_unowned(pool).await?;
                if unowned > 0 {
                    println!(
                        "\n{unowned} rows have no owner (claim them with: claim-legacy USERNAME)"
                    );
                }
            }
            Self::DeleteUser { username } => {
                let id = users::find_id(pool, &username).await?;
                println!(
                    "This permanently deletes '{username}' and all their sessions and exercises."
                );
                println!("Type the username to confirm:");
                let mut answer = String::new();
                std::io::stdin().lock().read_line(&mut answer)?;
                if answer.trim() != username {
                    return Err("Aborted.".into());
                }
                users::delete(pool, id).await?;
                println!("Deleted '{username}'.");
            }
            Self::ClaimLegacy { username } => {
                let id = users::find_id(pool, &username).await?;
                let n = users::claim_unowned(pool, id).await?;
                println!("Assigned {n} previously-unowned rows to '{username}'.");
            }
            Self::SeedExercises { username } => {
                let id = users::find_id(pool, &username).await?;
                let added = seed_exercises(pool, id).await?;
                println!("Added {added} exercises to '{username}'.");
            }
        }
        Ok(())
    }
}

/// Add the Lafay exercises whose names the user does not have yet; returns how many were added.
pub async fn seed_exercises(pool: &sqlx::PgPool, user_id: i32) -> Result<usize, AppError> {
    let library: Vec<Exercise> =
        serde_json::from_str(LAFAY_EXERCISES).map_err(AppError::internal)?;
    let existing: Vec<String> = docs::list::<Exercise>(pool, user_id)
        .await?
        .into_iter()
        .map(|e| e.doc.name)
        .collect();
    let mut added = 0;
    for ex in library.into_iter().filter(|e| !existing.contains(&e.name)) {
        docs::insert(pool, user_id, ex).await?;
        added += 1;
    }
    Ok(added)
}
