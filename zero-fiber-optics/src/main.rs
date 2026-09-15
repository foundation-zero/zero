mod app_config;
mod asyncapi;
mod config;
mod layout;
mod metrics;
mod mqtt;
mod parser;

use crate::app_config::AppConfig;
use crate::config::{load_config, Port, UdpChannels};
use crate::layout::{Layout, TopicMap};
use crate::metrics::{should_log_repeated, MqttMetrics, PortMetrics};
use crate::mqtt::{MqttHandler, PublishError};
use anyhow::{bail, Context, Result};
use clap::{Parser, Subcommand};
use log::{debug, error, info, warn};
use std::collections::HashMap;
use std::net::SocketAddr;
use std::sync::Arc;
use std::time::Duration;
use tokio::net::UdpSocket;
use tokio::sync::mpsc::error::TrySendError;
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::task::{JoinHandle, JoinSet};
use tokio_stream::wrappers::ReceiverStream;
use tokio_stream::StreamExt;

/// Fallback MQTT client ID, used when the pod name is not available.
const DEFAULT_CLIENT_ID: &str = "fiber-adapter";

/// How often the watchdog checks that each port is still receiving packets.
const WATCHDOG_INTERVAL: Duration = Duration::from_secs(10);

/// Number of watchdog ticks between counter summaries.
const SUMMARY_EVERY_TICKS: u32 = 6;

#[derive(Parser, Debug)]
#[command(name = "zero-fiber-optics")]
#[command(about = "UDP fiber optics adapter with MQTT publishing")]
struct Cli {
    #[arg(value_name = "CONFIG", default_value = "./example/config.xml")]
    config: String,

    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Run the adapter (default)
    Run,
    /// Print AsyncAPI schema and exit
    Asyncapi,
    /// Send an example UDP packet for the example config schema
    SendExample,
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();
    env_logger::init();

    let cli = Cli::parse();
    let config = read_runtime_config(&cli.config)?;

    match cli.command.unwrap_or(Commands::Run) {
        Commands::Asyncapi => {
            let app_config =
                AppConfig::load().context("Failed to load application configuration")?;
            let topic_map = TopicMap::new();
            let schema = asyncapi::build_schema(&config, &app_config.mqtt_prefix, &topic_map);
            println!("{}", serde_json::to_string_pretty(&schema)?);
        }
        Commands::Run => {
            let app_config =
                AppConfig::load().context("Failed to load application configuration")?;
            let client_id = mqtt_client_id();
            log_startup_config(&config, &app_config, &client_id);
            let mqtt_handler = create_mqtt_handler(&app_config, &client_id).await?;
            let mqtt_metrics = mqtt_handler.metrics();
            let topic_map = Arc::new(TopicMap::new());
            let (handles, port_metrics) = spawn_port_tasks(config.ports, mqtt_handler, topic_map);
            // The watchdog is deliberately kept out of `handles`. It loops forever,
            // so including it there would mean the process never exits: a failed
            // bind would leave a running-but-idle pod instead of one Kubernetes
            // restarts. Detached, it only runs as long as the port tasks do.
            let _watchdog = spawn_watchdog_task(port_metrics, mqtt_metrics);
            await_tasks(handles).await;
        }
        Commands::SendExample => {
            send_example_packet(&config).await?;
        }
    }

    Ok(())
}

fn packet_for_example_config(port: &Port) -> Result<Vec<u8>> {
    if port.variables.len() < 3 {
        bail!("Expected at least 3 variables (UnSignedInt32, SignedInt16, 8BitBoolRegister)");
    }

    if port.variables[0].var_type != "UnSignedInt32"
        || port.variables[1].var_type != "SignedInt16"
        || port.variables[2].var_type != "8BitBoolRegister"
    {
        bail!(
            "Config does not match example packet schema: expected [UnSignedInt32, SignedInt16, 8BitBoolRegister]"
        );
    }

    let packet_counter: u32 = 1;
    let angle_raw: i16 = 123;
    let status_flags: u8 = 0b0000_0001;

    let mut packet = Vec::with_capacity(7);
    packet.extend_from_slice(&packet_counter.to_be_bytes());
    packet.extend_from_slice(&angle_raw.to_be_bytes());
    packet.push(status_flags);
    Ok(packet)
}

fn target_ip_from_config(ip: &str) -> &str {
    match ip {
        "0.0.0.0" | "::" | "" => "127.0.0.1",
        _ => ip,
    }
}

async fn send_example_packet(config: &UdpChannels) -> Result<()> {
    let Some(port) = config.ports.first() else {
        bail!("Configuration has no ports")
    };

    let packet = packet_for_example_config(port)?;
    let target_ip = target_ip_from_config(&config.ip);
    let target = format!("{}:{}", target_ip, port.numport);

    let socket = UdpSocket::bind("0.0.0.0:0")
        .await
        .context("Failed to bind ephemeral UDP socket")?;
    let sent = socket
        .send_to(&packet, &target)
        .await
        .with_context(|| format!("Failed to send example packet to {}", target))?;

    info!(
        "Sent {}-byte example packet to {} for channel {}",
        sent, target, port.channel
    );
    println!(
        "Sent {}-byte example packet to {} for channel {}",
        sent, target, port.channel
    );
    Ok(())
}

fn read_runtime_config(config_path: &str) -> Result<crate::config::UdpChannels> {
    info!("Loading configuration from {}", config_path);
    let config_content = std::fs::read_to_string(config_path)
        .with_context(|| format!("Failed to read config file {}", config_path))?;

    load_config(&config_content).context("Failed to parse config XML")
}

/// Client ID for the MQTT connection.
///
/// Under Kubernetes `HOSTNAME` is the pod name, so each pod gets its own ID and
/// a rolling update cannot leave two replicas fighting over a single broker
/// session. Publish-only clients create no queues on the broker, so there is no
/// session state to orphan.
fn mqtt_client_id() -> String {
    std::env::var("HOSTNAME")
        .ok()
        .filter(|hostname| !hostname.is_empty())
        .unwrap_or_else(|| DEFAULT_CLIENT_ID.to_string())
}

/// Log what the process is about to connect to.
///
/// The `topic=` field makes a wrong config file or a wrong prefix obvious in the
/// first lines of the logs, rather than only being visible on the broker.
fn log_startup_config(config: &UdpChannels, app_config: &AppConfig, client_id: &str) {
    info!("UDP config: ip={} ports={}", config.ip, config.ports.len());
    for port in &config.ports {
        info!(
            "port {}: channel '{}' mode={} frequency={} variables={} \
             expected_packet_len={} topic='{}/{}'",
            port.numport,
            port.channel,
            port.mode.as_deref().unwrap_or("<unset>"),
            port.frequency
                .map(|frequency| frequency.to_string())
                .unwrap_or_else(|| "<unset>".to_string()),
            port.variables.len(),
            crate::parser::expected_packet_len(port),
            app_config.mqtt_prefix,
            port.channel,
        );
    }
    info!(
        "MQTT target {}:{} prefix '{}' client_id '{}'",
        app_config.mqtt_host, app_config.mqtt_port, app_config.mqtt_prefix, client_id
    );
    match app_config.credentials() {
        Some((username, _)) => info!("MQTT credentials: configured for user '{}'", username),
        None => info!("MQTT credentials: NONE (connecting anonymously)"),
    }
}

async fn create_mqtt_handler(app_config: &AppConfig, client_id: &str) -> Result<Arc<MqttHandler>> {
    info!(
        "Connecting to MQTT at {}:{}",
        app_config.mqtt_host, app_config.mqtt_port
    );
    let mqtt_handler = MqttHandler::new(
        &app_config.mqtt_host,
        app_config.mqtt_port,
        client_id,
        &app_config.mqtt_prefix,
        app_config.credentials(),
    )
    .await?;
    Ok(Arc::new(mqtt_handler))
}

fn spawn_udp_listener_task(
    addr: SocketAddr,
    port_num: u16,
    packet_tx: Sender<Vec<u8>>,
    metrics: Arc<PortMetrics>,
) -> JoinHandle<()> {
    tokio::spawn(async move {
        info!("Binding UDP listener on {}", addr);
        let socket = match UdpSocket::bind(addr).await {
            Ok(s) => s,
            Err(e) => {
                error!("Failed to bind to {}: {}", addr, e);
                return;
            }
        };

        let mut buf = vec![0u8; 65535];
        loop {
            match socket.recv_from(&mut buf).await {
                Ok((amt, src)) => {
                    metrics.incr_received();
                    if metrics.mark_first_packet() {
                        info!(
                            "port {}: first packet received ({} bytes from {})",
                            port_num, amt, src
                        );
                    }
                    debug!("port {}: received {} bytes from {}", port_num, amt, src);

                    // Never block on the hand-off. An awaited send would park this
                    // task as soon as the parser falls behind, and the kernel would
                    // then drop every datagram on a socket nobody is reading.
                    // Reserve before copying: `try_send` allocates and copies the
                    // datagram before discovering the queue is full, which is the
                    // hot path precisely while the parser is stalled.
                    match packet_tx.try_reserve() {
                        Ok(permit) => permit.send(buf[..amt].to_vec()),
                        Err(TrySendError::Full(())) => {
                            let dropped = metrics.incr_queue_dropped();
                            if should_log_repeated(dropped) {
                                warn!(
                                    "port {}: packet dropped, parser queue full \
                                     ({} dropped so far)",
                                    port_num, dropped
                                );
                            }
                        }
                        Err(TrySendError::Closed(())) => {
                            error!("port {}: parser task is gone, stopping listener", port_num);
                            break;
                        }
                    }
                }
                Err(e) => {
                    error!("Error receiving on port {}: {}", port_num, e);
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }
    })
}

fn spawn_parser_task(
    packet_rx: Receiver<Vec<u8>>,
    port_config: crate::config::Port,
    layout: Layout,
    mqtt_handler: Arc<MqttHandler>,
    topic_map: Arc<TopicMap>,
    metrics: Arc<PortMetrics>,
) -> JoinHandle<()> {
    tokio::spawn(async move {
        let channel = layout.channel.clone();
        let packet_stream = ReceiverStream::new(packet_rx);
        let mut variable_stream = crate::parser::parse_packet_stream(
            packet_stream,
            &port_config,
            &layout,
            metrics.clone(),
        );

        while let Some(parsed) = variable_stream.next().await {
            let vars = match parsed {
                Ok(vars) => vars,
                // parse_packet_stream has already logged and counted this.
                Err(_) => continue,
            };

            // A failed publish drops this packet. mqtt.rs logs the reason; the
            // counters below attribute the loss to this port.
            match mqtt_handler.publish(&channel, &vars, &topic_map).await {
                Ok(()) => {
                    metrics.incr_enqueued();
                }
                Err(PublishError::Timeout) => {
                    metrics.incr_publish_timeouts();
                }
                Err(_) => {
                    metrics.incr_publish_errors();
                }
            }
        }
    })
}

/// Counters for each configured UDP port, keyed by port number.
type PortMetricsByPort = Vec<(u16, Arc<PortMetrics>)>;

/// Spawn a UDP listener and parser task per configured port.
///
/// Returns the handles that keep the process alive, plus each port's counters
/// for the watchdog.
fn spawn_port_tasks(
    ports: Vec<crate::config::Port>,
    mqtt_handler: Arc<MqttHandler>,
    topic_map: Arc<TopicMap>,
) -> (Vec<JoinHandle<()>>, PortMetricsByPort) {
    let mut per_port_metrics = Vec::new();
    let handles: Vec<JoinHandle<()>> = ports
        .into_iter()
        .filter_map(|port_config| {
            let layout = Layout::from_port(&port_config);
            let addr_str = format!("0.0.0.0:{}", port_config.numport);
            let addr: SocketAddr = match addr_str.parse() {
                Ok(a) => a,
                Err(e) => {
                    error!("Invalid address {}: {}", addr_str, e);
                    return None;
                }
            };

            let metrics = PortMetrics::new();
            per_port_metrics.push((port_config.numport, metrics.clone()));

            let (packet_tx, packet_rx) = tokio::sync::mpsc::channel::<Vec<u8>>(256);
            let listener =
                spawn_udp_listener_task(addr, port_config.numport, packet_tx, metrics.clone());
            let parser = spawn_parser_task(
                packet_rx,
                port_config,
                layout,
                mqtt_handler.clone(),
                topic_map.clone(),
                metrics,
            );

            Some([listener, parser])
        })
        .flatten()
        .collect();

    (handles, per_port_metrics)
}

/// Warn when a port stops receiving packets, and report counters periodically.
///
/// The missing signal during the outage: the process had stopped reading its
/// socket entirely, and nothing in the logs said so.
fn spawn_watchdog_task(ports: PortMetricsByPort, mqtt_metrics: Arc<MqttMetrics>) -> JoinHandle<()> {
    tokio::spawn(async move {
        let mut ticker = tokio::time::interval(WATCHDOG_INTERVAL);
        // The first tick of an interval completes immediately.
        ticker.tick().await;

        let mut last_received: HashMap<u16, u64> = ports
            .iter()
            .map(|(port_num, metrics)| (*port_num, metrics.received()))
            .collect();
        let mut ticks = 0u32;

        loop {
            ticker.tick().await;

            for (port_num, metrics) in &ports {
                let received = metrics.received();
                let previous = last_received.get(port_num).copied().unwrap_or(received);
                if received == previous {
                    warn!(
                        "port {}: no UDP packets received in the last {:?} \
                         (total received {})",
                        port_num, WATCHDOG_INTERVAL, received
                    );
                }
                last_received.insert(*port_num, received);
            }

            ticks += 1;
            if ticks >= SUMMARY_EVERY_TICKS {
                ticks = 0;

                for (port_num, metrics) in &ports {
                    let snapshot = metrics.snapshot();
                    info!(
                        "port {} counters: received={} enqueued={} parse_errors={} \
                         length_mismatches={} queue_dropped={} publish_errors={} \
                         publish_timeouts={}",
                        port_num,
                        snapshot.received,
                        snapshot.enqueued,
                        snapshot.parse_errors,
                        snapshot.length_mismatches,
                        snapshot.queue_dropped,
                        snapshot.publish_errors,
                        snapshot.publish_timeouts,
                    );
                }

                // `enqueued` counts requests handed to the event loop; `acked`
                // counts PUBACKs from the broker. Enqueued pulling ahead of acked
                // is the signature of a broker that has stopped acknowledging.
                let snapshot = mqtt_metrics.snapshot();
                info!(
                    "mqtt counters: connects={} reconnects={} enqueued={} acked={} \
                     puback_denied={} publish_errors={} publish_timeouts={} \
                     server_disconnects={}",
                    snapshot.connects,
                    snapshot.reconnects,
                    snapshot.enqueued,
                    snapshot.acked,
                    snapshot.puback_denied,
                    snapshot.publish_errors,
                    snapshot.publish_timeouts,
                    snapshot.server_disconnects,
                );
            }
        }
    })
}

async fn await_tasks(handles: Vec<JoinHandle<()>>) {
    let mut join_set = JoinSet::new();
    for handle in handles {
        join_set.spawn(async move {
            if let Err(e) = handle.await {
                error!("Task failed: {}", e);
            }
        });
    }

    while let Some(result) = join_set.join_next().await {
        if let Err(e) = result {
            error!("Task monitor failed: {}", e);
        }
    }
}
