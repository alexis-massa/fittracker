//! FitTracker: the library behind the `fittracker` binary (split out so integration tests can build the
//! router and run the commands).

pub mod commands;
pub mod docs;
pub mod model;
pub mod routes;
pub mod users;

/// The app's migrations, embedded in the binary.
pub fn migrator() -> sqlx::migrate::Migrator {
    sqlx::migrate!()
}
