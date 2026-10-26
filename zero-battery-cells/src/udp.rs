use crate::cells::ModuleFrame;
use crate::decoder::Decoder;
use crate::mqtt::MqttGone;
use crate::throttle::log_event;
use log::{debug, error, info, warn};
use std::time::Duration;
use tokio::net::UdpSocket;
use tokio::sync::mpsc::error::TrySendError;
use tokio::sync::mpsc::Sender;

/// How often queue-full drops are logged, so an outage stays readable.
const DROP_LOG_INTERVAL: u64 = 1000;

/// Pause after a receive error before trying again.
const RECV_RETRY: Duration = Duration::from_millis(500);

/// Bind `0.0.0.0:port`, decode every datagram in place and queue its frames.
///
/// Datagrams are decoded straight out of the receive buffer, so nothing is
/// copied per datagram beyond what the reassembler keeps. Bursts are absorbed
/// by the kernel's socket buffer; decoding a pack takes microseconds, so the
/// socket is drained far faster than the PLCs fill it. Anything unknown or
/// undecodable is dropped with a logged reason.
///
/// The hand-off to the publisher never blocks. When the frame queue is full,
/// frames are dropped and counted instead of parking the reader: a stalled
/// socket would lose datagrams in the kernel either way.
///
/// The task ends when the frame queue closes (the publisher is gone) or the
/// bind fails; the pipeline then shuts the process down.
pub async fn run(port: u16, mut decoder: Decoder, frames: Sender<ModuleFrame<'static>>) {
    let address = format!("0.0.0.0:{}", port);
    info!("Binding UDP listener on {}", address);
    let socket = match UdpSocket::bind(&address).await {
        Ok(socket) => socket,
        Err(error) => {
            error!("Failed to bind UDP port {}: {}", port, error);
            return;
        }
    };

    let mut buffer = vec![0u8; 65535];
    let mut dropped = 0u64;
    loop {
        let (amount, source) = match socket.recv_from(&mut buffer).await {
            Ok(received) => received,
            Err(error) => {
                error!("Error receiving on {}: {}", address, error);
                tokio::time::sleep(RECV_RETRY).await;
                continue;
            }
        };
        debug!("received {} bytes from {}", amount, source);

        let decoded = match decoder.decode(source, &buffer[..amount]) {
            Ok(decoded) => decoded,
            Err(reason) => {
                debug!("dropping datagram from {}: {:#}", source, reason);
                continue;
            }
        };
        for frame in decoded.into_iter().flatten() {
            if let Err(gone) = sink_frame(&frames, frame, &mut dropped) {
                error!(
                    "UDP listener halts: {gone} ({} frame(s) unsent in total)",
                    dropped
                );
                return;
            }
        }
    }
}

/// Offer one frame to the publisher queue; `Ok` unless the publisher stopped.
///
/// Dropping beats stalling: the socket keeps being drained while the
/// publisher catches up.
fn sink_frame(
    frames: &Sender<ModuleFrame<'static>>,
    frame: ModuleFrame<'static>,
    dropped: &mut u64,
) -> Result<(), MqttGone> {
    match frames.try_reserve() {
        Ok(permit) => {
            permit.send(frame);
            Ok(())
        }
        Err(TrySendError::Full(())) => {
            *dropped += 1;
            if log_event(*dropped, DROP_LOG_INTERVAL) {
                warn!("frame queue full; dropped {} frame(s) so far", dropped);
            }
            Ok(())
        }
        Err(TrySendError::Closed(())) => Err(MqttGone),
    }
}
