mod cells;
mod config;
mod decoder;
mod mapping;
mod mqtt;
mod netvar;
mod nvl;
mod reassembly;
mod throttle;
mod udp;

use crate::cells::ModuleFrame;
use crate::config::PipelineConfig;
use crate::decoder::Decoder;
use crate::mqtt::{MqttGone, MqttPublisher, PublishError};
use crate::throttle::log_event;
use anyhow::{bail, Context, Result};
use clap::{Parser, Subcommand};
use futures_util::{StreamExt, TryStreamExt};
use log::{debug, error, info, warn};
use nom::multi::{length_data, many0};
use nom::number::complete::le_u32;
use std::net::SocketAddr;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::net::UdpSocket;
use tokio::sync::mpsc::Receiver;
use tokio::task::JoinSet;
use tokio_stream::wrappers::ReceiverStream;

/// Module-frame backlog between the UDP listener and the MQTT publisher, before drops.
///
/// Frames are fixed-size and heap-free, so the queue's footprint is bounded by
/// this capacity alone.
const FRAME_QUEUE: usize = 4096;

/// Warning throttle: warnings fire on the first occurrence and every Nth after it.
const WARNING_LOG_INTERVAL: u64 = 500;

#[derive(Parser, Debug)]
#[command(name = "zero-battery-cells")]
#[command(about = "CODESYS NetVar battery cell telemetry: UDP in, MQTT out")]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Run the UDP to MQTT pipeline (default)
    Run,
    /// Decode datagrams and print the frames; bring-up tool for PLC traffic
    Dissect {
        /// Read length-prefixed (u32 LE length + datagram) records
        /// from this file instead of binding UDP
        #[arg(long, value_name = "FILE")]
        file: Option<String>,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenvy::dotenv().ok();
    env_logger::init();

    let cli = Cli::parse();
    match cli.command.unwrap_or(Commands::Run) {
        Commands::Run => run().await,
        Commands::Dissect { file } => dissect(file.as_deref()).await,
    }
}

async fn run() -> Result<()> {
    let config = PipelineConfig::load().context("Failed to load configuration")?;
    let decoder = Decoder::load(&config)?;
    let publisher = MqttPublisher::new(&config.app, &mqtt_client_id())
        .await
        .context("Failed to start MQTT publisher")?;

    let (frame_tx, frame_rx) = tokio::sync::mpsc::channel(FRAME_QUEUE);

    let mut tasks = JoinSet::new();
    tasks.spawn(udp::run(config.app.udp_port, decoder, frame_tx));
    tasks.spawn(publish_task(publisher, frame_rx));
    await_tasks(&mut tasks).await
}

/// Module frames reach the broker.
///
/// Publish outcomes are try-stream items: only the MQTT client dying
/// (`Request`) terminates the pipeline, the same cascade as the UDP listener's
/// `MqttGone`. A stalled broker (`Timeout`) drops the message but keeps the
/// stream flowing, because rumqttc reconnects on its own.
///
/// The timeout counter is cumulative: unlike transient decode drops, publish
/// drops mean a broker stall in progress, and a running total reads clearer.
async fn publish_task(mqtt: MqttPublisher, frames: Receiver<ModuleFrame<'static>>) {
    let publisher = &mqtt;
    let timeouts = AtomicU64::new(0);
    let outcome = ReceiverStream::new(frames)
        .then(move |frame| async move { (frame, publisher.publish(&frame).await) })
        .map(|(frame, outcome)| match outcome {
            Ok(()) => {
                debug!(
                    "published pack {} string {} module {}",
                    frame.pack, frame.string, frame.module
                );
                Ok(())
            }
            Err(PublishError::Timeout) => {
                let occurrences = timeouts.fetch_add(1, Ordering::Relaxed) + 1;
                if log_event(occurrences, WARNING_LOG_INTERVAL) {
                    warn!(
                        "MQTT stalled on pack {}; dropped {} message(s) so far",
                        frame.pack, occurrences
                    );
                }
                Ok(())
            }
            // Already logged by the publisher; one frame lost, the stream flows on.
            Err(PublishError::Encode) => Ok(()),
            Err(PublishError::Request) => Err(MqttGone),
        })
        .try_for_each(|()| std::future::ready(Ok(())))
        .await;

    match outcome {
        Ok(()) => debug!("message stream closed"),
        Err(gone) => error!("publisher halts: {gone}"),
    }
}

/// Keep the pipeline tasks alive: end when a task stops, or after ctrl-c.
///
/// Any task ending means the pipeline is broken, so the rest are aborted (the
/// UDP listener may sit in `recv_from` indefinitely and would otherwise keep the
/// drain waiting) and the process exits with an error for the container
/// runtime to restart it. ctrl-c aborts everything and exits cleanly.
async fn await_tasks(tasks: &mut JoinSet<()>) -> Result<()> {
    let outcome = tokio::select! {
        biased;

        result = tasks.join_next() => match result {
            Some(Ok(())) => Err(anyhow::anyhow!("a pipeline task stopped")),
            Some(Err(e)) => Err(anyhow::anyhow!("a pipeline task failed: {}", e)),
            None => Ok(()),
        },

        _ = tokio::signal::ctrl_c() => {
            info!("Shutting down on ctrl-c");
            Ok(())
        }
    };
    tasks.abort_all();
    while let Some(result) = tasks.join_next().await {
        match result {
            Err(e) if !e.is_cancelled() => error!("Pipeline task failed during shutdown: {}", e),
            _ => {}
        }
    }
    outcome
}

/// A unique client id per process, so a restart cannot collide with a session
/// the broker still holds.
fn mqtt_client_id() -> String {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|since| since.as_nanos())
        .unwrap_or_default();
    format!("zero-battery-cells-{:05x}", nanos % 0xffff_ffff_ffff)
}

/// Decode datagrams without publishing: for bring-up against PLC traffic.
async fn dissect(recording: Option<&str>) -> Result<()> {
    let config = PipelineConfig::load().context("Failed to load configuration")?;
    let mut decoder = Decoder::load(&config)?;
    let prefix = &config.app.mqtt_prefix;
    match recording {
        Some(path) => dissect_file(&mut decoder, prefix, path),
        None => dissect_live(&mut decoder, prefix, config.app.udp_port).await,
    }
}

/// Replay a recording of `u32 LE length + datagram` records through the decoder.
fn dissect_file(decoder: &mut Decoder, prefix: &str, path: &str) -> Result<()> {
    let recording = std::fs::read(path).with_context(|| format!("Failed to read {}", path))?;
    let parsed: nom::IResult<&[u8], Vec<&[u8]>> = many0(length_data(le_u32))(recording.as_slice());
    let (rest, records) = parsed.map_err(|error| anyhow::anyhow!("{} in {}", error, path))?;
    if !rest.is_empty() {
        bail!(
            "truncated or malformed recording: {} unexpected byte(s) in {}",
            rest.len(),
            path
        );
    }

    let recorded_source: SocketAddr = "0.0.0.0:0"
        .parse()
        .context("invalid built-in sender address")?;
    for record in records {
        print_datagram(decoder, prefix, recorded_source, record);
    }
    Ok(())
}

/// Bind UDP and print streams as they arrive; ctrl-c ends the session.
async fn dissect_live(decoder: &mut Decoder, prefix: &str, port: u16) -> Result<()> {
    let address = format!("0.0.0.0:{}", port);
    let socket = UdpSocket::bind(&address)
        .await
        .with_context(|| format!("Failed to bind UDP port {}", address))?;
    println!("listening on {} (ctrl-c ends the session)", address);

    let mut buffer = vec![0u8; 65535];
    loop {
        tokio::select! {
            result = socket.recv_from(&mut buffer) => {
                match result {
                    Ok((amount, source)) => {
                        print_datagram(decoder, prefix, source, &buffer[..amount]);
                    }
                    Err(error) => println!("receive error: {}", error),
                }
            }
            _ = tokio::signal::ctrl_c() => break,
        }
    }
    Ok(())
}

/// Print one datagram's topic lines, or the reason it was dropped.
fn print_datagram(decoder: &mut Decoder, prefix: &str, source: SocketAddr, bytes: &[u8]) {
    match decoder.decode(source, bytes) {
        Ok(frames) => {
            for frame in frames.into_iter().flatten() {
                match serde_json::to_string(&frame) {
                    Ok(payload) => println!("{} {}", frame.topic(prefix), payload),
                    Err(error) => println!("{}: unserialisable: {}", frame.topic(prefix), error),
                }
            }
        }
        Err(reason) => println!("from {}: dropped: {:#}", source, reason),
    }
}
