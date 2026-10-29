use std::net::SocketAddr;
use std::sync::Arc;

use anyhow::{Context, Result};
use clap::Parser;
use log::{error, info};
use tokio::net::TcpListener;
use tokio::sync::oneshot;
use tokio::task::JoinHandle;

use zero_mqtt_graphql::api_model::Api;
use zero_mqtt_graphql::asyncapi::load_specs;
use zero_mqtt_graphql::cache::{TopicCache, spawn_eviction};
use zero_mqtt_graphql::config::AppConfig;
use zero_mqtt_graphql::graphql::build_schema;
use zero_mqtt_graphql::http::router;
use zero_mqtt_graphql::mqtt::{MqttConnection, MqttSubscriber};

/// A spawned MQTT subscriber task paired with a receiver that fires when
/// the task exits.
type MqttTask = (JoinHandle<()>, oneshot::Receiver<()>);

#[derive(Parser, Debug)]
#[command(name = "zero-mqtt-graphql")]
#[command(
    about = "MQTT-to-GraphQL bridge: consumes AsyncAPI specs, subscribes to MQTT topics, exposes live data via GraphQL"
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Command>,

    /// Directory containing AsyncAPI 3.0.0 JSON spec files
    #[arg(long, default_value = "specs", global = true)]
    spec_dir: String,
}

#[derive(Debug, clap::Subcommand, PartialEq)]
enum Command {
    /// Serve the GraphQL API (default)
    Serve,
    /// Listen to MQTT and log schema mismatches without starting the GraphQL server
    Listen,
    /// Validate AsyncAPI specs and sanitized GraphQL names without starting the server
    Validate,
    /// Print or export the GraphQL schema SDL without starting the server
    PrintSchema {
        /// Write the SDL to this file instead of stdout
        #[arg(long)]
        output: Option<String>,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();
    env_logger::init();

    let cli = Cli::parse();
    let config = AppConfig::load()?;
    let command = cli.command.unwrap_or(Command::Serve);
    let api = load_specs(&cli.spec_dir, command != Command::Validate)?;

    if api.is_empty() {
        info!("No MQTT topics found in spec directory '{}'", cli.spec_dir);
    }

    match command {
        Command::Validate => validate_command(&api)?,
        Command::PrintSchema { output } => export_sdl(&api, output.as_deref())?,
        Command::Listen => run_listen_only(&api, config).await?,
        Command::Serve => run_serve(config, &api).await?,
    }
    Ok(())
}

/// Strict validation for the `validate` subcommand: a missing or malformed
/// metadata file must fail so CI catches it (serve/listen stay lenient).
fn validate_command(api: &Api) -> Result<()> {
    println!("Validating the graphql schema...");

    zero_mqtt_graphql::graphql::validate_topics(api)?;

    let cache = Arc::new(TopicCache::new());

    let _schema = zero_mqtt_graphql::graphql::build_schema(api, &cache)?;

    println!("Validated — no sanitization collisions");
    Ok(())
}

/// Serve mode: expose the loaded specs as a GraphQL API backed by live MQTT
/// values, until Ctrl-C or an unexpected MQTT subscriber death.
async fn run_serve(config: AppConfig, api: &Api) -> Result<()> {
    let cache = Arc::new(TopicCache::with_ttl(
        config.default_ttl_secs,
        api.ttl_map(config.default_ttl_secs),
    ));
    spawn_eviction(cache.clone());

    let mut mqtt = spawn_mqtt_subscriber(&config, api, &cache)?;

    let schema = build_schema(api, &cache)?;
    let addr = SocketAddr::from(([0, 0, 0, 0], config.listen_port));
    info!("Listening on http://{addr}");
    let listener = TcpListener::bind(addr).await?;

    let sig = async {
        _ = tokio::signal::ctrl_c().await;
        info!("Received shutdown signal");
    };
    let server = axum::serve(listener, router(schema)).with_graceful_shutdown(sig);

    // `?` propagates a server error straight out of serve mode; otherwise
    // we only learn whether the MQTT subscriber died before the server.
    let mqtt_died = tokio::select! {
        result = server => { result?; false }
        () = mqtt_exit(&mut mqtt) => true,
    };

    match mqtt {
        Some((handle, _)) if mqtt_died => report_mqtt_subscriber_death(handle).await,
        Some((handle, _)) => reap_mqtt_subscriber(handle).await,
        None => {}
    }

    info!("Shutdown complete");
    Ok(())
}

/// Subscribe the MQTT subscriber to every concrete topic and group pattern.
///
/// Returns `None` without touching MQTT when there is nothing to subscribe
/// to; otherwise the returned receiver fires once the subscriber exits.
fn spawn_mqtt_subscriber(
    config: &AppConfig,
    api: &Api,
    cache: &Arc<TopicCache>,
) -> Result<Option<MqttTask>> {
    let mqtt_topics: Vec<String> = api.subscribe_topics();
    if mqtt_topics.is_empty() {
        info!("No MQTT topics to subscribe to");
        return Ok(None);
    }

    let connection = MqttConnection {
        host: &config.mqtt_host,
        port: config.mqtt_port,
        username: config.mqtt_username.as_deref(),
        password: config.mqtt_password.as_deref(),
    };
    let mut sub =
        MqttSubscriber::new_with_mode(&connection, cache.clone(), false, api.validators())?;
    sub.set_pending_subscriptions(&mqtt_topics);
    Ok(Some(spawn_subscriber(sub)))
}

/// Spawn a prepared subscriber, returning its task handle plus its exit
/// signal.
fn spawn_subscriber(sub: MqttSubscriber) -> MqttTask {
    let (dead_tx, dead_rx) = oneshot::channel::<()>();
    let handle = tokio::spawn(async move {
        sub.run().await;
        let _ = dead_tx.send(());
    });
    (handle, dead_rx)
}

/// Resolves once the MQTT subscriber exits; never resolves when none was
/// spawned.
async fn mqtt_exit(mqtt: &mut Option<MqttTask>) {
    match mqtt {
        Some((_, dead_rx)) => {
            let _ = dead_rx.await;
        }
        None => std::future::pending().await,
    }
}

/// Await an MQTT subscriber that died on its own — aborting it first when
/// it is still running — and report how it ended.
async fn report_mqtt_subscriber_death(handle: JoinHandle<()>) {
    if !handle.is_finished() {
        handle.abort();
    }
    match handle.await {
        Err(e) if e.is_panic() => {
            error!("MQTT subscriber panicked: {e} — shutting down");
        }
        Err(_) => error!("MQTT subscriber task cancelled unexpectedly — shutting down"),
        Ok(()) => error!("MQTT subscriber task exited unexpectedly — shutting down"),
    }
}

/// Abort an MQTT subscriber task and await its end after a deliberate
/// shutdown.
async fn reap_mqtt_subscriber(handle: JoinHandle<()>) {
    handle.abort();
    match handle.await {
        Err(e) if e.is_cancelled() => info!("MQTT subscriber task cancelled"),
        Ok(()) => info!("MQTT subscriber task exited"),
        Err(e) => error!("MQTT subscriber task panicked: {e}"),
    }
}

async fn run_listen_only(api: &Api, config: AppConfig) -> Result<()> {
    info!("Running in listen-only mode — validating payloads, not serving GraphQL");

    let cache = Arc::new(TopicCache::new());
    let mqtt_topics: Vec<String> = api.subscribe_topics();

    let connection = MqttConnection {
        host: &config.mqtt_host,
        port: config.mqtt_port,
        username: config.mqtt_username.as_deref(),
        password: config.mqtt_password.as_deref(),
    };
    let mut sub = MqttSubscriber::new_with_mode(&connection, cache, true, api.validators())?;
    sub.set_pending_subscriptions(&mqtt_topics);

    let (handle, dead_rx) = spawn_subscriber(sub);

    let sig = async {
        _ = tokio::signal::ctrl_c().await;
        info!("Received shutdown signal");
    };

    let interrupted = tokio::select! {
        () = sig => true,
        _ = dead_rx => false,
    };

    if interrupted {
        info!("Shutting down listen-only mode");
        reap_mqtt_subscriber(handle).await;
    } else {
        error!("MQTT subscriber task exited unexpectedly — shutting down");
        report_mqtt_subscriber_death(handle).await;
    }

    info!("Shutdown complete");
    Ok(())
}

/// Print the schema SDL to stdout, or write it to `output` when given.
///
/// Used by the `print-schema` subcommand so the SDL can be exported for
/// client codegen without starting the server.
fn export_sdl(api: &Api, output: Option<&str>) -> Result<()> {
    info!("Exporting graphql schema sdl.");

    let cache = Arc::new(TopicCache::new());
    let schema = build_schema(api, &cache)?;
    let sdl = schema.sdl();
    match output {
        Some(path) => {
            std::fs::write(path, &sdl).with_context(|| format!("writing schema to '{path}'"))?;
            info!("Wrote GraphQL schema ({} bytes) to {}", sdl.len(), path);
        }
        None => println!("{sdl}"),
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use zero_mqtt_graphql::api_model::GraphqlType;
    use zero_mqtt_graphql::roas_asyncapi::OperationAction;
    use zero_mqtt_graphql::{
        api_model::{ApiModel, TopicDef},
        topic_map::TopicMap,
    };

    fn sample_api() -> Api {
        let topics = vec![TopicDef {
            topic: "test/topic".to_string(),
            fields: BTreeMap::from_iter(vec![("x".to_string(), GraphqlType::Float)]),
            payload_schema_ref: None,
            action: OperationAction::Send,
            ttl_secs: 300,
        }];

        Api::new(vec![ApiModel::new(
            "test".to_string(),
            TopicMap::new(),
            topics,
            vec![],
            TopicMap::new(),
        )])
    }

    #[test_log::test]
    fn test_export_sdl_to_file() {
        let dir = std::env::temp_dir().join("mqtt-graphql-print-schema-test");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("schema.graphql");

        export_sdl(&sample_api(), path.to_str()).unwrap();

        let sdl = std::fs::read_to_string(&path).unwrap();
        assert!(sdl.contains("type Query"), "{sdl}");
        assert!(sdl.contains("testTopic"), "{sdl}");

        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test_log::test]
    fn test_export_sdl_stdout_does_not_fail() {
        export_sdl(&sample_api(), None).unwrap();
    }
}
