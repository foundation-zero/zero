mod app_config;
mod asyncapi;
mod config;
mod layout;
mod mqtt;
mod parser;

use crate::app_config::AppConfig;
use crate::config::load_config;
use crate::layout::{Layout, TopicMap};
use crate::mqtt::MqttHandler;
use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use log::{debug, error, info};
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::UdpSocket;
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::task::JoinHandle;
use tokio_stream::wrappers::ReceiverStream;
use tokio_stream::StreamExt;

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
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();
    env_logger::init();

    let cli = Cli::parse();
    let app_config = AppConfig::load().context("Failed to load application configuration")?;
    let config = read_runtime_config(&cli.config)?;

    match cli.command.unwrap_or(Commands::Run) {
        Commands::Asyncapi => {
            let topic_map = TopicMap::new();
            let schema = asyncapi::build_schema(&config, &app_config.mqtt_prefix, &topic_map);
            println!("{}", serde_json::to_string_pretty(&schema)?);
        }
        Commands::Run => {
            let mqtt_handler = create_mqtt_handler(&app_config).await?;
            let topic_map = Arc::new(TopicMap::new());
            let handles = spawn_port_tasks(config.ports, mqtt_handler, topic_map);
            await_tasks(handles).await;
        }
    }

    Ok(())
}

fn read_runtime_config(config_path: &str) -> Result<crate::config::UdpChannels> {
    info!("Loading configuration from {}", config_path);
    let config_content = std::fs::read_to_string(config_path)
        .with_context(|| format!("Failed to read config file {}", config_path))?;

    load_config(&config_content).context("Failed to parse config XML")
}

async fn create_mqtt_handler(app_config: &AppConfig) -> Result<Arc<MqttHandler>> {
    info!(
        "Connecting to MQTT at {}:{}",
        app_config.mqtt_host, app_config.mqtt_port
    );
    let mqtt_handler = MqttHandler::new(
        &app_config.mqtt_host,
        app_config.mqtt_port,
        "fiber-adapter",
        &app_config.mqtt_prefix,
        app_config.mqtt_username.as_deref(),
        app_config.mqtt_password.as_deref(),
    )
    .await?;
    Ok(Arc::new(mqtt_handler))
}

fn spawn_udp_listener_task(
    addr: SocketAddr,
    port_num: u16,
    packet_tx: Sender<Vec<u8>>,
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
                Ok((amt, _src)) => {
                    debug!("Received {} bytes on port {}", amt, port_num);
                    let _ = packet_tx.send(buf[..amt].to_vec()).await;
                }
                Err(e) => {
                    error!("Error receiving on port {}: {}", port_num, e);
                    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
                }
            }
        }
    })
}

fn spawn_parser_publisher_task(
    packet_rx: Receiver<Vec<u8>>,
    port_config: crate::config::Port,
    layout: Layout,
    mqtt_handler: Arc<MqttHandler>,
    topic_map: Arc<TopicMap>,
) -> JoinHandle<()> {
    tokio::spawn(async move {
        let channel = layout.channel.clone();
        let packet_stream = ReceiverStream::new(packet_rx);
        let mut variable_stream =
            crate::parser::parse_packet_stream(packet_stream, &port_config, &layout);

        while let Some(parsed) = variable_stream.next().await {
            match parsed {
                Ok(vars) => {
                    if let Err(e) = mqtt_handler.publish(&channel, &vars, &topic_map).await {
                        error!("Failed to publish MQTT message: {}", e);
                    }
                }
                Err(e) => {
                    error!(
                        "Failed to parse packet on port {}: {}",
                        port_config.numport, e
                    );
                }
            }
        }
    })
}

fn spawn_port_tasks(
    ports: Vec<crate::config::Port>,
    mqtt_handler: Arc<MqttHandler>,
    topic_map: Arc<TopicMap>,
) -> Vec<JoinHandle<()>> {
    let mut handles = Vec::new();

    for port_config in ports {
        let layout = Layout::from_port(&port_config);
        let addr_str = format!("0.0.0.0:{}", port_config.numport);
        let addr: SocketAddr = match addr_str.parse() {
            Ok(a) => a,
            Err(e) => {
                error!("Invalid address {}: {}", addr_str, e);
                continue;
            }
        };

        let (packet_tx, packet_rx) = tokio::sync::mpsc::channel::<Vec<u8>>(256);
        handles.push(spawn_udp_listener_task(
            addr,
            port_config.numport,
            packet_tx,
        ));
        handles.push(spawn_parser_publisher_task(
            packet_rx,
            port_config,
            layout,
            mqtt_handler.clone(),
            topic_map.clone(),
        ));
    }

    handles
}

async fn await_tasks(handles: Vec<JoinHandle<()>>) {
    // TODO: does tokio not having a function/macro for this?
    for handle in handles {
        if let Err(e) = handle.await {
            error!("Task failed: {}", e);
        }
    }
}
