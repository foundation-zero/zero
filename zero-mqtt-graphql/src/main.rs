use std::net::SocketAddr;
use std::sync::Arc;

use anyhow::{Context, Result};
use clap::Parser;
use log::{error, info, warn};
use tokio::net::TcpListener;
use tokio::sync::oneshot;
use tokio::task::JoinHandle;

use zero_mqtt_graphql::asyncapi::{
    load_specs_and_groups, LoadedSpecs, ObjectTypeDef, TopicDef, TopicGroupDef, ValidatorSpec,
};
use zero_mqtt_graphql::cache::TopicCache;
use zero_mqtt_graphql::config::AppConfig;
use zero_mqtt_graphql::graphql::{build_schema, SchemaInputs, TopicPublisher};
use zero_mqtt_graphql::http::router;
use zero_mqtt_graphql::metadata::{load_metadata, MetadataFile};
use zero_mqtt_graphql::modules_view::{load_module_views, ModuleView};
use zero_mqtt_graphql::mqtt::{MqttConnection, MqttPublisher, MqttSubscriber};
use zero_mqtt_graphql::mutations_view::{load_mutations, ModuleMutations};
use zero_mqtt_graphql::simulation_view::SimulationView;

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

#[derive(Debug, clap::Subcommand)]
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
    let LoadedSpecs {
        topics,
        groups,
        object_types,
        validators,
    } = load_specs_and_groups(&cli.spec_dir)?;
    match cli.command.unwrap_or(Command::Serve) {
        Command::Validate => validate_command(&cli.spec_dir, &topics, &groups, &object_types)?,
        Command::PrintSchema { output } => {
            let metadata = load_metadata_or_empty(&cli.spec_dir);
            export_sdl(
                &topics,
                &groups,
                &object_types,
                &metadata,
                output.as_deref(),
            )?;
        }
        Command::Listen => {
            run_listen_only(cli.spec_dir, topics, groups, validators, config).await?
        }
        Command::Serve => {
            run_serve(
                &cli.spec_dir,
                config,
                topics,
                groups,
                object_types,
                validators,
            )
            .await?
        }
    }
    Ok(())
}

/// Strict validation for the `validate` subcommand: a missing or malformed
/// metadata file must fail so CI catches it (serve/listen stay lenient).
fn validate_command(
    spec_dir: &str,
    topics: &[TopicDef],
    groups: &[TopicGroupDef],
    object_types: &[ObjectTypeDef],
) -> Result<()> {
    if topics.is_empty() && groups.is_empty() {
        anyhow::bail!("no topics found in '{spec_dir}'");
    }
    let metadata = load_metadata(spec_dir)?;
    zero_mqtt_graphql::graphql::validate_topics(topics)?;
    let cache = Arc::new(TopicCache::new());
    let _schema = build_schema(
        cache,
        SchemaInputs {
            topics,
            groups,
            metadata: &metadata,
            object_types,
            ..Default::default()
        },
    )?;
    println!(
        "Validated {} topic(s), {} group(s), {} composite object type(s) and {} metadata file(s) from '{}' — no sanitization collisions",
        topics.len(),
        groups.len(),
        object_types.len(),
        metadata.len(),
        spec_dir
    );
    Ok(())
}

/// Serve mode: expose the loaded specs as a GraphQL API backed by live MQTT
/// values, until Ctrl-C or an unexpected MQTT subscriber death.
async fn run_serve(
    spec_dir: &str,
    config: AppConfig,
    mut topics: Vec<TopicDef>,
    mut groups: Vec<TopicGroupDef>,
    object_types: Vec<ObjectTypeDef>,
    validator_specs: Vec<ValidatorSpec>,
) -> Result<()> {
    let metadata = load_metadata_or_empty(spec_dir);
    let mut module_views = load_module_views_or_empty(spec_dir);
    // Mutations (write-path) are only served when ENABLE_MUTATIONS is set; the
    // specs load either way so a misconfig is visible, but with the toggle off
    // no publisher is built and the schema stays read-only.
    let mut mutations = load_mutations_or_empty(spec_dir);
    // The simulation spec (status/inputs/outputs relay, directives, input
    // mutations). Read side is always served; the write side follows
    // ENABLE_MUTATIONS like the module mutations.
    let mut simulation = load_simulation_view_or_none(spec_dir);
    // When PREFIX_STRATEGY=runtime, rewrite every subscribe/cache/publish
    // topic from the spec prefix to the live-broker prefix before anything
    // consumes them, so the subscribe set, the cache keys, and the resolver
    // reads all move together. No-op under the default build_time strategy,
    // which bakes the prefix into the spec instead.
    let rewriter = zero_mqtt_graphql::prefix::PrefixRewriter::from_config(&config);
    if !rewriter.is_noop() {
        info!("Prefix strategy: runtime — rewriting spec topic prefixes to live-broker prefixes");
        rewriter.apply_to_topics(&mut topics);
        rewriter.apply_to_groups(&mut groups);
        rewriter.apply_to_views(&mut module_views);
        rewriter.apply_to_mutations(&mut mutations);
        if let Some(sim) = &mut simulation {
            rewriter.apply_to_simulation(sim);
        }
    }
    // The whole-object read sections (controlValues/parameters/controllerState)
    // are each one MQTT topic carrying the section object; subscribe to them so
    // the nested resolvers can read them from the cache. Always subscribed (the
    // read-path is on regardless of ENABLE_MUTATIONS); deduped against the
    // mutation state topics, which include the same `.../parameters` topic.
    let mut extra_topics = module_section_topics(&module_views);
    if let Some(sim) = &simulation {
        for topic in sim.read_topics() {
            if !extra_topics.contains(&topic) {
                extra_topics.push(topic);
            }
        }
    }
    if config.enable_mutations {
        for topic in mutation_state_topics(&mutations) {
            if !extra_topics.contains(&topic) {
                extra_topics.push(topic);
            }
        }
    }
    if topics.is_empty() {
        info!("No MQTT topics found in spec directory '{spec_dir}'");
    }

    let cache = Arc::new(TopicCache::from_definitions(
        &topics,
        &groups,
        config.default_ttl_secs,
    ));
    zero_mqtt_graphql::graphql::spawn_eviction(cache.clone());
    let (mut mqtt, publisher) = spawn_mqtt_subscriber(
        &config,
        &topics,
        &groups,
        &validator_specs,
        &cache,
        &extra_topics,
    )?;

    // The write side is served only with ENABLE_MUTATIONS; without it no
    // publisher reaches the schema and it stays read-only.
    let publisher = publisher.filter(|_| config.enable_mutations);
    if publisher.is_some() {
        info!(
            "Mutations enabled: serving {} module(s) of mutations{}",
            mutations.iter().filter(|m| !m.mutations.is_empty()).count(),
            if simulation.is_some() {
                " + simulation directives/input mutations"
            } else {
                ""
            }
        );
    }
    let schema = build_schema(
        cache,
        SchemaInputs {
            topics: &topics,
            groups: &groups,
            metadata: &metadata,
            object_types: &object_types,
            module_views: &module_views,
            mutations: &mutations,
            simulation: simulation.as_ref(),
            publisher,
            computed_mode: config.computed_mode,
            enable_optional_sensor_values: config.enable_optional_sensor_values,
        },
    )?;
    let addr = SocketAddr::from(([0, 0, 0, 0], config.listen_port));
    info!("Listening on http://{}", addr);
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
        _ = mqtt_exit(&mut mqtt) => true,
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
    topics: &[TopicDef],
    groups: &[TopicGroupDef],
    validator_specs: &[ValidatorSpec],
    cache: &Arc<TopicCache>,
    extra_topics: &[String],
) -> Result<(Option<MqttTask>, Option<Arc<dyn TopicPublisher>>)> {
    // `extra_topics` are the mutation state topics (e.g.
    // `controller_prefix/<module>/parameters`) whose cached objects the
    // mutations read-modify-republish; subscribing to them keeps that state
    // fresh. Empty unless mutations are enabled.
    let mqtt_topics: Vec<String> = topics
        .iter()
        .map(|t| t.topic.clone())
        .chain(groups.iter().map(|g| g.pattern.clone()))
        .chain(extra_topics.iter().cloned())
        .collect();
    if mqtt_topics.is_empty() {
        info!("No MQTT topics to subscribe to");
        return Ok((None, None));
    }

    let connection = MqttConnection {
        host: &config.mqtt_host,
        port: config.mqtt_port,
        username: config.mqtt_username.as_deref(),
        password: config.mqtt_password.as_deref(),
    };
    let mut sub = MqttSubscriber::new_with_mode(
        connection,
        cache.clone(),
        false,
        config.strict_validation,
        validator_specs,
    )?;
    sub.set_pending_subscriptions(&mqtt_topics);
    // A publish handle on the same client, for serving mutations. Cheap to make
    // even when mutations are off (the schema builder just won't use it).
    let publisher: Arc<dyn TopicPublisher> = Arc::new(MqttPublisher::new(sub.client()));
    Ok((Some(spawn_subscriber(sub)), Some(publisher)))
}

/// Load the simulation spec leniently (serve mode): a malformed file is logged
/// and the simulation surface is just not served.
fn load_simulation_view_or_none(spec_dir: &str) -> Option<SimulationView> {
    match zero_mqtt_graphql::simulation_view::load_simulation_view(spec_dir) {
        Ok(Some(sim)) => {
            info!(
                "Loaded simulation view: {} simulation(s), {} input mutation(s)",
                sim.simulations.len(),
                sim.mutations().count()
            );
            Some(sim)
        }
        Ok(None) => None,
        Err(e) => {
            warn!("Failed to load simulation view from '{spec_dir}': {e:#}");
            None
        }
    }
}

/// Load `*-mutations.json` write-path specs from the spec dir. Lenient, like
/// `load_module_views_or_empty`: a missing or malformed file is logged and
/// ignored, leaving the schema read-only.
fn load_mutations_or_empty(spec_dir: &str) -> Vec<ModuleMutations> {
    match load_mutations(spec_dir) {
        Ok(mutations) => {
            let count: usize = mutations.iter().map(|m| m.mutations.len()).sum();
            if count > 0 {
                info!(
                    "Loaded {count} mutation(s) from {} module(s)",
                    mutations.len()
                );
            }
            mutations
        }
        Err(e) => {
            info!("No mutation specs loaded from '{}': {}", spec_dir, e);
            Vec::new()
        }
    }
}

/// The distinct state topics the mutations read from, so the subscriber can
/// keep their cached objects current.
fn mutation_state_topics(mutations: &[ModuleMutations]) -> Vec<String> {
    let mut topics: Vec<String> = mutations
        .iter()
        .flat_map(|m| m.mutations.iter().map(|def| def.state_topic.clone()))
        .collect();
    topics.sort();
    topics.dedup();
    topics
}

/// The distinct whole-object section topics (controlValues/parameters/
/// controllerState) across all module views, so the subscriber caches them for
/// the nested read resolvers.
fn module_section_topics(views: &[ModuleView]) -> Vec<String> {
    let mut topics: Vec<String> = views
        .iter()
        .flat_map(|v| {
            [&v.control_values, &v.parameters, &v.controller_state]
                .into_iter()
                .flatten()
                .map(|s| s.topic.clone())
                .chain(v.control_mode.iter().map(|cm| cm.topic.clone()))
        })
        .filter(|t| !t.is_empty())
        .collect();
    topics.sort();
    topics.dedup();
    topics
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
            error!("MQTT subscriber panicked: {} — shutting down", e)
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

async fn run_listen_only(
    spec_dir: String,
    topics: Vec<TopicDef>,
    groups: Vec<TopicGroupDef>,
    validator_specs: Vec<ValidatorSpec>,
    config: AppConfig,
) -> Result<()> {
    if topics.is_empty() && groups.is_empty() {
        anyhow::bail!("no topics found in '{}' — nothing to listen for", spec_dir);
    }
    info!(
        "Running in listen-only mode: {} topic(s), {} group(s) from '{}' — validating payloads, not serving GraphQL",
        topics.len(),
        groups.len(),
        spec_dir
    );

    let cache = Arc::new(TopicCache::new());
    let mqtt_topics: Vec<String> = topics
        .iter()
        .map(|t| t.topic.clone())
        .chain(groups.iter().map(|g| g.pattern.clone()))
        .collect();

    let connection = MqttConnection {
        host: &config.mqtt_host,
        port: config.mqtt_port,
        username: config.mqtt_username.as_deref(),
        password: config.mqtt_password.as_deref(),
    };
    // listen-only never caches, so strict validation is moot here.
    let mut sub = MqttSubscriber::new_with_mode(connection, cache, true, false, &validator_specs)?;
    sub.set_pending_subscriptions(&mqtt_topics);

    let (handle, dead_rx) = spawn_subscriber(sub);

    let sig = async {
        _ = tokio::signal::ctrl_c().await;
        info!("Received shutdown signal");
    };

    let interrupted = tokio::select! {
        _ = sig => true,
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

/// Load topic metadata from the spec dir.
///
/// A missing or malformed file is logged and otherwise ignored; the
/// `validate` subcommand loads it strictly instead.
fn load_metadata_or_empty(spec_dir: &str) -> Vec<MetadataFile> {
    match load_metadata(spec_dir) {
        Ok(files) => {
            let topics: usize = files.iter().map(|f| f.topics.len()).sum();
            info!("Loaded {} metadata file(s) ({topics} entries)", files.len());
            files
        }
        Err(e) => {
            info!("No topic metadata loaded from '{}': {}", spec_dir, e);
            Vec::new()
        }
    }
}

/// Load `*-module.json` view specs from the spec dir.
///
/// A missing or malformed file is logged and ignored (lenient, like
/// `load_metadata_or_empty`); with none present the `modules { … }` query just
/// isn't exposed.
fn load_module_views_or_empty(spec_dir: &str) -> Vec<ModuleView> {
    match load_module_views(spec_dir) {
        Ok(views) => {
            if !views.is_empty() {
                let fields: usize = views.iter().map(|v| v.sensor_values.len()).sum();
                info!(
                    "Loaded {} module-view spec(s) ({fields} sensor field(s))",
                    views.len()
                );
            }
            views
        }
        Err(e) => {
            info!("No module-view specs loaded from '{}': {}", spec_dir, e);
            Vec::new()
        }
    }
}

/// Print the schema SDL to stdout, or write it to `output` when given.
///
/// Used by the `print-schema` subcommand so the SDL can be exported for
/// client codegen without starting the server.
fn export_sdl(
    topics: &[zero_mqtt_graphql::asyncapi::TopicDef],
    groups: &[zero_mqtt_graphql::asyncapi::TopicGroupDef],
    object_types: &[ObjectTypeDef],
    metadata: &[MetadataFile],
    output: Option<&str>,
) -> Result<()> {
    if topics.is_empty() && groups.is_empty() {
        anyhow::bail!("no topics found — nothing to export");
    }
    let cache = Arc::new(TopicCache::new());
    let schema = build_schema(
        cache,
        SchemaInputs {
            topics,
            groups,
            metadata,
            object_types,
            ..Default::default()
        },
    )?;
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
    use super::*;
    use zero_mqtt_graphql::asyncapi::{FieldDef, TopicDef};

    fn sample_topics() -> Vec<TopicDef> {
        vec![TopicDef {
            topic: "test/topic".to_string(),
            fields: vec![FieldDef {
                name: "x".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        }]
    }

    #[test]
    fn test_export_sdl_to_file() {
        let dir = std::env::temp_dir().join("mqtt-graphql-print-schema-test");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("schema.graphql");

        export_sdl(&sample_topics(), &[], &[], &[], path.to_str()).unwrap();

        let sdl = std::fs::read_to_string(&path).unwrap();
        assert!(sdl.contains("type Query"), "{sdl}");
        assert!(sdl.contains("testTopic"), "{sdl}");

        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn test_export_sdl_empty_specs_error() {
        let err = export_sdl(&[], &[], &[], &[], None).unwrap_err();
        assert!(err.to_string().contains("no topics found"), "{err}");
    }

    #[test]
    fn test_export_sdl_stdout_does_not_fail() {
        export_sdl(&sample_topics(), &[], &[], &[], None).unwrap();
    }
}
