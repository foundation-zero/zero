mod app_config;
mod asyncapi;
mod config;
mod layout;
mod mqtt;
mod parser;

use crate::app_config::AppConfig;
use crate::config::{load_config, Port, UdpChannels};
use crate::layout::{Layout, TopicMap};
use crate::mqtt::MqttHandler;
use anyhow::{bail, Context, Result};
use clap::{Parser, Subcommand};
use log::{error, info};
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::UdpSocket;
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::task::{JoinHandle, JoinSet};
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
            let mqtt_handler = create_mqtt_handler(&app_config).await?;
            let topic_map = Arc::new(TopicMap::new());
            let handles = spawn_port_tasks(config.ports, mqtt_handler, topic_map);
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

fn spawn_parser_task(
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
    ports
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

            let (packet_tx, packet_rx) = tokio::sync::mpsc::channel::<Vec<u8>>(256);
            let listener = spawn_udp_listener_task(addr, port_config.numport, packet_tx);
            let parser = spawn_parser_task(
                packet_rx,
                port_config,
                layout,
                mqtt_handler.clone(),
                topic_map.clone(),
            );

            Some([listener, parser])
        })
        .flatten()
        .collect()
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
