use std::str::FromStr;

use clap::{Parser, Subcommand};
use config::Config;
use futures::{FutureExt, TryStreamExt};
use tokio::{select, time::Instant};

use crate::stub::Interrogator;

mod client;
mod msg;
mod stub;

#[derive(Parser)]
#[command(name = "zero-mast-deformation")]
#[command(about = "A CLI tool for mast deformation analysis")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Stub {
        /// Command address
        #[arg(long, default_value = "127.0.0.1:51971")]
        cmd_addr: String,
        /// Peak address
        #[arg(long, default_value = "127.0.0.1:51972")]
        peak_addr: String,
        /// Spectrum address
        #[arg(long, default_value = "127.0.0.1:51973")]
        spectrum_addr: String,
        /// Duration to run the stub server in seconds, empty for infinite
        #[arg(long)]
        duration: Option<u64>,
    },
    Peaks {
        /// Address of the peaks server
        #[arg(long, default_value = "127.0.0.1:51972")]
        addr: String,
        /// Duration to run the peaks client in seconds, empty for infinite
        #[arg(long)]
        duration: Option<u64>,
    },
}

#[derive(serde::Deserialize)]
pub struct Settings {
    pub interrogators: Vec<InterrogatorSettings>,
}

#[derive(serde::Deserialize, Clone, Debug, PartialEq, Eq)]
pub enum SignalFrequency {
    #[serde(rename = "1")]
    Hz1,
    #[serde(rename = "10")]
    Hz10,
    #[serde(rename = "100")]
    Hz100,
    #[serde(rename = "1000")]
    Hz1000,
}
impl FromStr for SignalFrequency {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "1" => Ok(SignalFrequency::Hz1),
            "10" => Ok(SignalFrequency::Hz10),
            "100" => Ok(SignalFrequency::Hz100),
            "1000" => Ok(SignalFrequency::Hz1000),
            _ => Err(()),
        }
    }
}

#[derive(serde::Deserialize, Clone)]
pub struct InterrogatorSettings {
    pub ip: String,
    pub frequency: SignalFrequency,
    pub channels: Vec<ChannelSettings>,
}

#[derive(serde::Deserialize, Clone)]
pub struct ChannelSettings {
    pub number: u32,
    pub fbgs: Vec<FbgSettings>,
}

#[derive(serde::Deserialize, Clone)]
pub struct FbgSettings {
    pub name: String,
    pub wavelength: f64,
    pub delay: f32,
}

#[tokio::main]
async fn main() {
    env_logger::init();
    let settings = Config::builder()
        .add_source(config::File::with_name("./fbgs.yaml"))
        .build()
        .unwrap();
    let settings = settings.try_deserialize::<Settings>().unwrap();
    let cli = Cli::parse();

    match cli.command {
        Commands::Stub {
            cmd_addr,
            peak_addr,
            spectrum_addr,
            duration,
        } => {
            let mut controller = Interrogator::new(
                &cmd_addr,
                &peak_addr,
                &spectrum_addr,
                &settings.interrogators[0],
            )
            .await
            .serve()
            .await
            .unwrap();
            controller.enable_peak_data_streaming().await.unwrap();
            log::info!("Running stub server...");

            let timeout = if let Some(d) = duration {
                tokio::time::sleep(tokio::time::Duration::from_secs(d)).boxed()
            } else {
                futures::future::pending().boxed()
            };
            select! {
                _ = tokio::signal::ctrl_c() => {},
                _ = timeout => {},
            }
            log::info!("Shutting down...");
        }
        Commands::Peaks { addr, duration } => {
            let mut stream = client::PeaksClient::stream_peaks(&addr).await.unwrap();
            log::info!("Connecting to peaks server at {}", addr);
            let start = Instant::now();
            while let Some(peaks) = stream.try_next().await.unwrap() {
                log::info!("Received peaks: {:?}", peaks);
                if let Some(d) = duration {
                    if start.elapsed().as_secs() >= d {
                        break;
                    }
                }
            }
        }
    }
}
