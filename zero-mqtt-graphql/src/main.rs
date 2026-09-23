use std::net::SocketAddr;
use std::sync::Arc;

use anyhow::{Context, Result};
use clap::Parser;
use log::{error, info};
use tokio::net::TcpListener;
use tokio::sync::oneshot;
use tokio::task::JoinHandle;

use zero_mqtt_graphql::asyncapi::{
    load_specs_and_groups, LoadedSpecs, ObjectTypeDef, TopicDef, TopicGroupDef, ValidatorSpec,
};
use zero_mqtt_graphql::cache::TopicCache;
use zero_mqtt_graphql::config::AppConfig;
use zero_mqtt_graphql::extension::GraphqlExtension;
use zero_mqtt_graphql::graphql::{build_schema, PublishFuture, SchemaInputs, TopicPublisher};
use zero_mqtt_graphql::http::router;
use zero_mqtt_graphql::metadata::{load_metadata, MetadataFile};
use zero_mqtt_graphql::mqtt::{MqttConnection, MqttPublisher, MqttSubscriber};

/// A spawned MQTT subscriber task paired with a receiver that fires when
/// the task exits.
type MqttTask = (JoinHandle<()>, oneshot::Receiver<()>);
/// The subscriber task (if anything to subscribe to) and the mutations' publisher.
type MqttSide = (Option<MqttTask>, Option<Arc<dyn TopicPublisher>>);

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
        mut topics,
        mut groups,
        object_types,
        mut validators,
        mut extension,
        ..
    } = load_specs_and_groups(&cli.spec_dir)?;
    // Under PREFIX_STRATEGY=runtime every topic moves to the live-broker prefix together.
    let rewriter = zero_mqtt_graphql::prefix::PrefixRewriter::from_config(&config);
    if !rewriter.is_noop() {
        info!("Prefix strategy: runtime — rewriting spec topic prefixes to live-broker prefixes");
        rewriter.apply_to_topics(&mut topics);
        rewriter.apply_to_groups(&mut groups);
        rewriter.apply_to_validators(&mut validators);
        if let Some(extension) = &mut extension {
            rewriter.apply_to_extension(extension);
        }
    }
    match cli.command.unwrap_or(Command::Serve) {
        Command::Validate => validate_command(
            &cli.spec_dir,
            &config,
            &topics,
            &groups,
            &object_types,
            extension.as_ref(),
        )?,
        Command::PrintSchema { output } => {
            let metadata = metadata_or_empty(&cli.spec_dir, extension.as_ref());
            let schema = offline_schema(
                &config,
                &topics,
                &groups,
                &object_types,
                &metadata,
                extension.as_ref(),
            )?;
            export_sdl(&schema, output.as_deref())?;
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
                extension,
            )
            .await?
        }
    }
    Ok(())
}

/// Strict validation for `validate`: a bad metadata file fails, and the schema
/// is built as `serve` would.
fn validate_command(
    spec_dir: &str,
    config: &AppConfig,
    topics: &[TopicDef],
    groups: &[TopicGroupDef],
    object_types: &[ObjectTypeDef],
    extension: Option<&GraphqlExtension>,
) -> Result<()> {
    if topics.is_empty() && groups.is_empty() {
        anyhow::bail!("no topics found in '{spec_dir}'");
    }
    let mut metadata = load_metadata(spec_dir)?;
    metadata.extend(
        extension
            .map(|e| e.metadata_files.clone())
            .unwrap_or_default(),
    );
    zero_mqtt_graphql::graphql::validate_topics(topics)?;
    let _schema = offline_schema(config, topics, groups, object_types, &metadata, extension)?;
    let (views, lifecycles, mutations) = extension
        .map(|e| (e.views.len(), e.lifecycles.len(), e.mutation_count()))
        .unwrap_or_default();
    println!(
        "Validated {} topic(s), {} group(s), {} composite object type(s), {} metadata group(s), {} view(s), {} lifecycle(s) and {} mutation(s) from '{}' — no sanitization collisions",
        topics.len(),
        groups.len(),
        object_types.len(),
        metadata.len(),
        views,
        lifecycles,
        mutations,
        spec_dir
    );
    Ok(())
}

/// The publisher of a schema built without a broker: every publish fails.
struct OfflinePublisher;

impl TopicPublisher for OfflinePublisher {
    fn publish(&self, topic: String, _payload: String) -> PublishFuture {
        Box::pin(async move { anyhow::bail!("no broker connection: cannot publish to '{topic}'") })
    }
}

/// The schema `serve` would build from these specs, without a broker.
fn offline_schema(
    config: &AppConfig,
    topics: &[TopicDef],
    groups: &[TopicGroupDef],
    object_types: &[ObjectTypeDef],
    metadata: &[MetadataFile],
    extension: Option<&GraphqlExtension>,
) -> Result<async_graphql::dynamic::Schema> {
    let empty = GraphqlExtension::default();
    let extension = extension.unwrap_or(&empty);
    let publisher: Option<Arc<dyn TopicPublisher>> = config
        .enable_mutations
        .then(|| Arc::new(OfflinePublisher) as Arc<dyn TopicPublisher>);
    build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics,
            groups,
            metadata,
            object_types,
            views: &extension.views,
            lifecycles: &extension.lifecycles,
            publisher,
            enable_optional_sensor_values: config.enable_optional_sensor_values,
        },
    )
}

/// Serve mode: expose the loaded specs as a GraphQL API backed by live MQTT
/// values, until Ctrl-C or an unexpected MQTT subscriber death.
async fn run_serve(
    spec_dir: &str,
    config: AppConfig,
    topics: Vec<TopicDef>,
    groups: Vec<TopicGroupDef>,
    object_types: Vec<ObjectTypeDef>,
    validator_specs: Vec<ValidatorSpec>,
    extension: Option<GraphqlExtension>,
) -> Result<()> {
    let extension = extension.unwrap_or_default();
    let metadata = metadata_or_empty(spec_dir, Some(&extension));
    // Whole-object view sections are read from the cache, so always subscribe.
    let extra_topics = extension.read_topics(config.enable_mutations);
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

    let publisher = publisher.filter(|_| config.enable_mutations);
    if publisher.is_some() {
        info!(
            "Mutations enabled: serving {} mutation(s) and directive(s)",
            extension.mutation_count()
        );
    }
    let schema = build_schema(
        cache,
        SchemaInputs {
            topics: &topics,
            groups: &groups,
            metadata: &metadata,
            object_types: &object_types,
            views: &extension.views,
            lifecycles: &extension.lifecycles,
            publisher,
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
) -> Result<MqttSide> {
    // `extra_topics`: mutation state topics read-modify-republished by mutations.
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
    let publisher: Arc<dyn TopicPublisher> = Arc::new(MqttPublisher::new(sub.client()));
    Ok((Some(spawn_subscriber(sub)), Some(publisher)))
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

/// Every metadata group: the `*-metadata.json` files plus the extension's `{field}` groups.
fn metadata_or_empty(spec_dir: &str, extension: Option<&GraphqlExtension>) -> Vec<MetadataFile> {
    let mut metadata = load_metadata_or_empty(spec_dir);
    if let Some(extension) = extension {
        metadata.extend(extension.metadata_files.iter().cloned());
    }
    metadata
}

/// Print the schema SDL to stdout, or write it to `output` when given.
///
/// Used by the `print-schema` subcommand so the SDL can be exported for
/// client codegen without starting the server.
fn export_sdl(schema: &async_graphql::dynamic::Schema, output: Option<&str>) -> Result<()> {
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

    /// The defaults every knob falls back to when its env var is unset.
    fn config(enable_mutations: bool) -> AppConfig {
        let mut config: AppConfig = serde_json::from_value(serde_json::json!({})).unwrap();
        config.enable_mutations = enable_mutations;
        config
    }

    /// One view with a parameters section and its `setField` mutation.
    fn extension() -> GraphqlExtension {
        use roas_asyncapi::v3_0::operation::OperationAction;
        use std::collections::BTreeMap;
        use zero_mqtt_graphql::asyncapi::{OperationDef, OperationIndex};
        use zero_mqtt_graphql::extension::{parse_extension, EXTENSION_KEY, EXTENSION_VERSION};

        let reference = serde_json::json!({"$ref": "#/components/schemas/Parameters"});
        let components = serde_json::json!({"schemas": {"Parameters": {
            "type": "object", "properties": {"CoolingFlow": {"type": "number"}}}}});
        let op = |action, address: &str| OperationDef {
            action,
            address: address.to_string(),
            pattern: address.to_string(),
            document: "doc.json".to_string(),
            payload: Some(reference.clone()),
            parameter_schemas: BTreeMap::new(),
        };
        let operations = OperationIndex::from([
            ("p".to_string(), op(OperationAction::Send, "ctl/parameters")),
            (
                "s".to_string(),
                op(OperationAction::Receive, "ctl/parameters/set"),
            ),
        ]);
        let root = BTreeMap::from([(
            EXTENSION_KEY.to_string(),
            serde_json::json!({
                "version": EXTENSION_VERSION,
                "types": {"ThrustersParametersType": {"schema": reference}},
                "views": [{"gql": "modules", "typeName": "ControlModules", "members": [{
                    "gql": "thrusters", "typeName": "ThrustersControlModule",
                    "sections": [{"kind": "object", "gql": "parameters",
                        "typeName": "ThrustersParametersType", "operation": {"operation": "p"}}],
                    "mutations": [{"gql": "thrustersParameterSetCoolingFlow", "kind": "setField",
                        "argName": "value", "key": "CoolingFlow", "returns": "parameters",
                        "state": {"operation": "p"}, "target": {"operation": "s"}}]
                }]}]
            }),
        )]);
        let mut extension = parse_extension(Some(&root), Some(&components), "doc.json")
            .unwrap()
            .unwrap();
        extension.resolve(&operations, &[]).unwrap();
        extension
    }

    #[test]
    fn test_export_sdl_to_file() {
        let dir = std::env::temp_dir().join("mqtt-graphql-print-schema-test");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("schema.graphql");

        let schema = offline_schema(&config(false), &sample_topics(), &[], &[], &[], None).unwrap();
        export_sdl(&schema, path.to_str()).unwrap();

        let sdl = std::fs::read_to_string(&path).unwrap();
        assert!(sdl.contains("type Query"), "{sdl}");
        assert!(sdl.contains("testTopic"), "{sdl}");

        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn test_export_sdl_stdout_does_not_fail() {
        let schema = offline_schema(&config(false), &sample_topics(), &[], &[], &[], None).unwrap();
        export_sdl(&schema, None).unwrap();
    }

    /// The offline schema is the served one: views are always in, the
    /// mutation side follows ENABLE_MUTATIONS.
    #[test]
    fn test_offline_schema_includes_views_and_mutations_per_config() {
        let ext = extension();
        let read_only =
            offline_schema(&config(false), &sample_topics(), &[], &[], &[], Some(&ext)).unwrap();
        let sdl = read_only.sdl();
        assert!(sdl.contains("modules: ControlModules"), "{sdl}");
        assert!(!sdl.contains("type Mutation"), "{sdl}");

        let writable =
            offline_schema(&config(true), &sample_topics(), &[], &[], &[], Some(&ext)).unwrap();
        let sdl = writable.sdl();
        assert!(
            sdl.contains("thrustersParameterSetCoolingFlow(value: Float!)"),
            "{sdl}"
        );
    }

    #[tokio::test]
    async fn test_offline_publisher_rejects_every_publish() {
        let err = OfflinePublisher
            .publish("a/b".into(), "{}".into())
            .await
            .unwrap_err();
        assert!(err.to_string().contains("no broker connection"), "{err}");
    }
}
