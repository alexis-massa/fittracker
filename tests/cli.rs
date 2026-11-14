//! The binary's own subcommands, run as a user would (stdin, stdout). Run with `just test`.

mod common;

use std::io::Write;
use std::process::{Command, Stdio};

use common::{PASSWORD, pool, test_url, user};

/// Run `fittracker ARGS` against the test database, feeding `stdin`; returns (success, stdout).
fn run(args: &[&str], stdin: &str) -> (bool, String) {
    let mut child = Command::new(env!("CARGO_BIN_EXE_fittracker"))
        .args(args)
        .env("DATABASE_URL", test_url())
        .env("APP_DOMAIN", "app.test")
        .env("RUST_LOG", "warn")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(stdin.as_bytes())
        .unwrap();
    let out = child.wait_with_output().unwrap();
    (
        out.status.success(),
        String::from_utf8_lossy(&out.stdout).into_owned(),
    )
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn user_commands() {
    let pool = pool().await;
    let name = format!("cli-{}", std::process::id());
    let (ok, out) = run(&["create-user", &name], &format!("{PASSWORD}\n"));
    assert!(ok && out.contains("Created user"), "{out}");
    assert!(
        !run(&["create-user", &name], &format!("{PASSWORD}\n")).0,
        "duplicate refused"
    );
    assert!(
        !run(&["create-user", "ok-name"], "short\n").0,
        "short password refused"
    );

    assert!(run(&["set-password", &name], "another password\n").0);
    assert!(
        run(&["seed-exercises", &name], "")
            .1
            .contains("Added 26 exercises")
    );
    assert!(
        run(&["seed-exercises", &name], "")
            .1
            .contains("Added 0 exercises"),
        "skips existing names"
    );
    let (_, listing) = run(&["list-users"], "");
    assert!(
        listing.contains(&format!("{name:<20} 0 sessions, 26 exercises")),
        "{listing}"
    );

    assert!(
        !run(&["delete-user", &name], "wrong\n").0,
        "needs the typed name"
    );
    assert!(run(&["delete-user", &name], &format!("{name}\n")).0);
    assert!(fittracker::users::find_id(&pool, &name).await.is_err());
}

#[tokio::test]
#[ignore = "needs Postgres: run `just test`"]
async fn claim_legacy_gives_unowned_rows_to_a_user() {
    let pool = pool().await;
    let name = user(&pool, "claim").await;
    sqlx::query!("INSERT INTO exercises (doc) VALUES ('{\"name\": \"orphan\"}')")
        .execute(&pool)
        .await
        .unwrap();
    assert!(fittracker::users::count_unowned(&pool).await.unwrap() >= 1);
    let (ok, out) = run(&["claim-legacy", &name], "");
    assert!(ok && out.contains("previously-unowned rows"), "{out}");
    assert_eq!(fittracker::users::count_unowned(&pool).await.unwrap(), 0);
}
