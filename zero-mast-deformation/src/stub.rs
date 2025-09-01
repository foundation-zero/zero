use crate::msg::{Command, CommandMsg, PeaksReply, Reply};
use crate::{ChannelSettings, FbgSettings, InterrogatorSettings, SignalFrequency};

use std::marker::PhantomData;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Duration;

use anyhow::Result;
use futures::TryStreamExt;
use futures::{Stream, StreamExt};
use futures_rx::RxExt;
use tokio::io::AsyncWriteExt;
use tokio::net::tcp::OwnedReadHalf;
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::{broadcast, mpsc, watch};
use tokio::task::JoinHandle;
use tokio_stream::wrappers::errors::BroadcastStreamRecvError;
use tokio_stream::wrappers::{BroadcastStream, IntervalStream, ReceiverStream};
use tokio_util::bytes::{Buf, BytesMut};
use tokio_util::codec::{Decoder, FramedRead};

pub(crate) struct Interrogator {
    command_addr: String,
    peak_addr: String,
    spectrum_addr: String,
    settings: SweepGeneratorOptions,
}

enum DataStreamerState<T: DataSender> {
    Inactive(DataStreamer<Inactive, T>),
    Serving(DataStreamer<Serving, T>),
}

impl Interrogator {
    pub(crate) async fn new(
        command_addr: &str,
        peak_addr: &str,
        spectrum_addr: &str,
        settings: &InterrogatorSettings,
    ) -> Interrogator {
        Interrogator {
            command_addr: command_addr.to_owned(),
            peak_addr: peak_addr.to_owned(),
            spectrum_addr: spectrum_addr.to_owned(),
            settings: settings.into(),
        }
    }

    pub(crate) async fn serve(&mut self) -> Result<Controller> {
        let listener = TcpListener::bind(self.command_addr.as_str()).await?;

        let (tx_command, rx_command) = mpsc::channel(10);

        {
            let tx_command = tx_command.clone();
            tokio::spawn(async move {
                Interrogator::listen_for_commands(listener, tx_command).await;
            });
        }

        let (tx_settings, rx_settings) = watch::channel(self.settings.clone());
        let mut sweeps = tokio_stream::wrappers::WatchStream::new(rx_settings)
            .switch_map(SweepGenerator::generate);

        let (tx_sweep, rx_peak_sweep) = broadcast::channel::<Sweep>(16);
        let rx_spectrum_sweep = tx_sweep.subscribe();
        let sweep_sender = tokio::spawn(async move {
            loop {
                while let Some(sweep) = sweeps.next().await {
                    tx_sweep.send(sweep).unwrap();
                }
            }
        });

        let peak_addr = self.peak_addr.clone();
        let spectrum_addr = self.spectrum_addr.clone();
        let task = tokio::spawn(async move {
            Interrogator::handle_commands(
                peak_addr.as_str(),
                rx_peak_sweep,
                spectrum_addr.as_str(),
                rx_spectrum_sweep,
                rx_command,
                tx_settings,
                sweep_sender,
            )
            .await;
        });
        Ok(Controller {
            tx: tx_command,
            task,
        })
    }

    async fn listen_for_commands(addr: TcpListener, tx: mpsc::Sender<Command>) {
        loop {
            let (socket, _) = addr.accept().await.unwrap();
            log::info!("Accepted connection from {:?}", socket.peer_addr());
            let (rx, _tx) = socket.into_split();
            let rx_command = CommandReceiver::serve(rx).await;
            let tx = tx.clone();
            tokio::spawn(async move {
                rx_command
                    .for_each(|cmd| async {
                        log::info!("Received command: {:?}", cmd);
                        tx.send(cmd).await.unwrap();
                    })
                    .await;
                log::info!("Command connection closed");
            });
        }
    }

    async fn handle_commands(
        peak_addr: &str,
        rx_peak_sweep: broadcast::Receiver<Sweep>,
        spectrum_addr: &str,
        rx_spectrum_sweep: broadcast::Receiver<Sweep>,
        rx_command: mpsc::Receiver<Command>,
        tx_settings: watch::Sender<SweepGeneratorOptions>,
        sweep_sender: JoinHandle<()>,
    ) {
        let mut peak_streamer = DataStreamerState::Inactive(
            DataStreamer::<Inactive, PeakSender>::new(peak_addr, rx_peak_sweep),
        );
        let mut spectrum_streamer =
            DataStreamerState::Inactive(DataStreamer::<Inactive, SpectrumSender>::new(
                spectrum_addr,
                rx_spectrum_sweep,
            ));
        let mut rx_stream = ReceiverStream::new(rx_command);

        while let Some(cmd) = rx_stream.next().await {
            match cmd {
                Command::EnablePeakDataStreaming => {
                    if let DataStreamerState::Inactive(peak) = peak_streamer {
                        log::info!("Starting peak data streaming");
                        peak_streamer = DataStreamerState::Serving(peak.serve().await.unwrap());
                    }
                }
                Command::DisablePeakDataStreaming => {
                    if let DataStreamerState::Serving(peak) = peak_streamer {
                        log::info!("Stopping peak data streaming");
                        peak_streamer = DataStreamerState::Inactive(peak.stop().await.unwrap());
                    }
                }
                Command::EnableFullSpectrumDataStreaming => {
                    if let DataStreamerState::Inactive(spectrum) = spectrum_streamer {
                        log::info!("Starting spectrum data streaming");
                        spectrum_streamer =
                            DataStreamerState::Serving(spectrum.serve().await.unwrap());
                    }
                }
                Command::DisableFullSpectrumDataStreaming => {
                    if let DataStreamerState::Serving(spectrum) = spectrum_streamer {
                        log::info!("Stopping spectrum data streaming");
                        spectrum_streamer =
                            DataStreamerState::Inactive(spectrum.stop().await.unwrap());
                    }
                }
                Command::SetLaserScanSpeed(f) => {
                    log::info!("Set laser scan speed to {:?}", f);
                    let new_settings = {
                        let settings = tx_settings.borrow();
                        SweepGeneratorOptions {
                            frequency: f,
                            channels: settings.channels.clone(),
                        }
                    };
                    tx_settings.send(new_settings).unwrap();
                }
                Command::GetLaserScanSpeed => {
                    // TODO: Process commands within socket context to be able to reply
                    // let settings = tx_settings.borrow();
                    // log::info!("Current laser scan speed: {:?}", settings.frequency);
                }

                Command::Stop => {
                    sweep_sender.abort();
                    break;
                }
            }
        }
    }
}
pub(crate) struct Controller {
    tx: mpsc::Sender<Command>,
    task: JoinHandle<()>,
}

impl Controller {
    #[allow(dead_code)]
    pub(crate) async fn enable_peak_data_streaming(&mut self) -> Result<()> {
        self.tx.send(Command::EnablePeakDataStreaming).await?;
        Ok(())
    }

    #[allow(dead_code)]
    pub(crate) async fn disable_peak_data_streaming(&mut self) -> Result<()> {
        self.tx.send(Command::DisablePeakDataStreaming).await?;
        Ok(())
    }

    #[allow(dead_code)]
    pub(crate) async fn enable_full_spectrum_data_streaming(&mut self) -> Result<()> {
        self.tx
            .send(Command::EnableFullSpectrumDataStreaming)
            .await?;
        Ok(())
    }

    #[allow(dead_code)]
    pub(crate) async fn disable_full_spectrum_data_streaming(&mut self) -> Result<()> {
        self.tx
            .send(Command::DisableFullSpectrumDataStreaming)
            .await?;
        Ok(())
    }

    #[allow(dead_code)]
    pub(crate) async fn wait_for_completion(self) -> Result<()> {
        self.task.await?;
        Ok(())
    }
}

pub struct CommandMsgDecoder;
impl Decoder for CommandMsgDecoder {
    type Item = CommandMsg;
    type Error = anyhow::Error;

    fn decode(&mut self, src: &mut BytesMut) -> Result<Option<Self::Item>, Self::Error> {
        match CommandMsg::parse(src) {
            Ok((remaining, msg)) => {
                let used = src.len() - remaining.len();
                src.advance(used);
                Ok(Some(msg))
            }
            Err(nom::Err::Incomplete(_)) => Ok(None),
            Err(e) => Err(e.map_input(|i| i.to_vec()))?,
        }
    }
}

struct CommandReceiver;
impl CommandReceiver {
    async fn serve(rx: OwnedReadHalf) -> impl Stream<Item = Command> {
        FramedRead::new(rx, CommandMsgDecoder).filter_map(|result| async {
            match result {
                Ok(cmd_msg) => Some(cmd_msg.command),
                Err(e) => {
                    log::error!("Failed to decode command: {:?}", e);
                    None
                }
            }
        })
    }
}

#[derive(Clone, Debug)]
pub struct Sweep {
    pub timestamp: std::time::SystemTime,
    pub serial_number: u64,
    pub peaks: Vec<Peak>,
}

#[derive(Clone, Debug)]
pub struct Peak {
    pub channel: u8,
    pub wavelength: f64,
}

#[derive(Clone)]
pub struct SweepGeneratorOptions {
    frequency: SignalFrequency,
    channels: Vec<ChannelOptions>,
}

impl From<&InterrogatorSettings> for SweepGeneratorOptions {
    fn from(value: &InterrogatorSettings) -> Self {
        SweepGeneratorOptions {
            frequency: value.frequency.clone(),
            channels: value.channels.iter().map(Into::into).collect(),
        }
    }
}
#[derive(Clone)]
pub struct ChannelOptions {
    #[allow(dead_code)]
    active: bool,
    fbgs: Vec<FbgOptions>,
}
impl From<&ChannelSettings> for ChannelOptions {
    fn from(value: &ChannelSettings) -> Self {
        ChannelOptions {
            active: true,
            fbgs: value.fbgs.iter().map(Into::into).collect(),
        }
    }
}
#[derive(Clone)]
pub struct FbgOptions {
    wavelength: f64,
    #[allow(dead_code)]
    delay: f32,
}
impl From<&FbgSettings> for FbgOptions {
    fn from(value: &FbgSettings) -> Self {
        FbgOptions {
            wavelength: value.wavelength,
            delay: value.delay,
        }
    }
}

static SERIAL_NUMBER: AtomicU64 = AtomicU64::new(0);

struct SweepGenerator;
impl SweepGenerator {
    fn generate(options: SweepGeneratorOptions) -> impl Stream<Item = Sweep> {
        let interval = match options.frequency {
            SignalFrequency::Hz1 => Duration::from_secs(1),
            SignalFrequency::Hz10 => Duration::from_millis(100),
            SignalFrequency::Hz100 => Duration::from_millis(10),
            SignalFrequency::Hz1000 => Duration::from_millis(1),
        };
        let interval = tokio::time::interval(interval);

        let channels = options.channels.clone();
        IntervalStream::new(interval).map(move |_| {
            let peaks = channels.iter().enumerate().flat_map(|(ch, ch_opts)| {
                ch_opts.fbgs.iter().map(move |fbg| Peak {
                    channel: (ch + 1) as u8,
                    wavelength: fbg.wavelength,
                })
            });
            Sweep {
                timestamp: std::time::SystemTime::now(),
                serial_number: SERIAL_NUMBER.fetch_add(1, Ordering::Relaxed),
                peaks: peaks.collect(),
            }
        })
    }
}

trait DataSender {
    fn send(
        sweep: &Sweep,
        socket: &mut TcpStream,
    ) -> impl std::future::Future<Output = Result<()>> + Send;
}

struct Inactive;
struct Serving {
    commands_tx: broadcast::Sender<Event>,
    task: JoinHandle<()>,
}
struct DataStreamer<State, S: DataSender> {
    peak_addr: String,
    signals: broadcast::Receiver<Sweep>,
    state: State,
    _marker: PhantomData<S>,
}

impl<S: DataSender> DataStreamer<Inactive, S> {
    fn new(peak_addr: &str, signals: broadcast::Receiver<Sweep>) -> DataStreamer<Inactive, S> {
        DataStreamer {
            peak_addr: peak_addr.to_owned(),
            signals,
            state: Inactive {},
            _marker: PhantomData,
        }
    }

    async fn serve(self) -> Result<DataStreamer<Serving, S>> {
        let (commands_tx, commands_rx) = broadcast::channel::<Event>(10);
        let listener = TcpListener::bind(&self.peak_addr).await?;
        let signals = self.signals.resubscribe();

        let task = tokio::spawn(async move {
            loop {
                let (mut socket, _) = listener.accept().await.unwrap();
                let signals = signals.resubscribe();
                let commands_rx = commands_rx.resubscribe();

                tokio::spawn(async move {
                    let sweeps = BroadcastStream::new(signals.resubscribe()).map_ok(Event::Sweep);
                    let stops = BroadcastStream::new(commands_rx);
                    let mut events = {
                        use tokio_stream::StreamExt;
                        sweeps.merge(stops)
                    };

                    while let Some(event) = events.next().await {
                        match event {
                            Ok(Event::Sweep(sweep)) => {
                                S::send(&sweep, &mut socket).await.unwrap();
                            }
                            Ok(Event::Stop) => {
                                break;
                            }
                            Err(BroadcastStreamRecvError::Lagged(n)) => {
                                log::warn!("Lagged {} messages", n);
                            }
                        }
                    }
                });
            }
        });
        Ok(DataStreamer {
            peak_addr: self.peak_addr,
            signals: self.signals,
            state: Serving { commands_tx, task },
            _marker: PhantomData,
        })
    }
}

impl<S: DataSender> DataStreamer<Serving, S> {
    async fn stop(self) -> Result<DataStreamer<Inactive, S>> {
        self.state.commands_tx.send(Event::Stop)?;
        self.state.task.await?;
        Ok(DataStreamer {
            peak_addr: self.peak_addr,
            signals: self.signals,
            state: Inactive {},
            _marker: PhantomData,
        })
    }
}

#[derive(Clone, Debug)]
enum Event {
    Sweep(Sweep),
    Stop,
}

#[allow(dead_code)]
struct SpectrumSender;

impl DataSender for SpectrumSender {
    async fn send(_sweep: &Sweep, socket: &mut TcpStream) -> Result<()> {
        // TODO: Serialize the sweep data and send it over the socket
        socket.write_all("a".as_bytes()).await?;
        Ok(())
    }
}

#[allow(dead_code)]
struct PeakSender;

impl DataSender for PeakSender {
    async fn send(sweep: &Sweep, socket: &mut TcpStream) -> Result<()> {
        let peaks_reply: PeaksReply = sweep.into();
        let reply: Reply = (&peaks_reply).into();

        reply.write_async(socket).await?;
        Ok(())
    }
}
