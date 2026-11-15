use std::process::ExitCode;

use clap::{Parser, Subcommand};
use fittracker::{commands, migrator, routes};
use pi_common::cli::{self, App, Common, Context};
use pi_common::server::Security;

#[derive(Parser)]
#[command(
    version,
    about = "FitTracker: a workout tracker built around timed set/rest circuits"
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    #[command(flatten)]
    Common(Common),
    #[command(flatten)]
    App(commands::Command),
}

#[tokio::main]
async fn main() -> ExitCode {
    pi_common::telemetry::init();
    match Cli::parse().command {
        Command::Common(command) => {
            let app = App {
                migrator: migrator(),
                security: Security::default(),
                build: routes::build,
            };
            cli::run(command, app).await
        }
        Command::App(command) => {
            cli::report(async { command.run(Context::from_env(migrator()).await?).await }.await)
        }
    }
}
