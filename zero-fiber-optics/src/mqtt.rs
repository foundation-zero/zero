use crate::layout::{packet_payload, TopicMap, Variable};
use crate::metrics::{should_log_repeated, MqttMetrics};
use crate::readiness::{write_termination_message, Readiness};
use log::{debug, error, info, warn};
use rumqttc::{
    AsyncClient, ConnectReturnCode, ConnectionError, Event, EventLoop, Incoming, MqttOptions, QoS,
};
use std::sync::Arc;
use std::time::Duration;

/// MQTT keep-alive interval: how quickly a dead connection is noticed.
const KEEP_ALIVE: Duration = Duration::from_secs(15);

/// Largest packet sent or accepted. A production payload (390 readings) is
/// roughly 16 KB of JSON, over rumqttc's 10 KB default.
const MAX_PACKET_SIZE: usize = 65536;

/// Socket send buffer: a few packets, so a broker that stops reading blocks the
/// next flush within a second and the flush timeout fires. Left to Linux's
/// autotuning it holds every unacknowledged publish, and the stall only shows
/// when a ping goes unanswered, after twice the keep-alive.
const SEND_BUFFER_SIZE: u32 = 65536;

/// Capacity of the channel between publishers and the event loop.
const REQUEST_CHANNEL_CAPACITY: usize = 10;

/// How long a publish may wait for room in the request channel before it is
/// abandoned.
///
/// A healthy enqueue takes microseconds, so reaching this means the event loop
/// is not draining requests - a stalled or blocked broker. Bounding it is what
/// keeps that from wedging the UDP reader waiting behind it.
const PUBLISH_TIMEOUT: Duration = Duration::from_secs(5);

/// First reconnect delay before the event loop backs off.
const INITIAL_BACKOFF: Duration = Duration::from_secs(1);
/// Reconnect delay ceiling: the client reconnects within this long after the broker is back.
const MAX_BACKOFF: Duration = Duration::from_secs(30);

/// Refusals such as bad credentials before giving up, in about 3 minutes of
/// backoff. A booting broker can refuse logins too, so the first is not final.
const PERMANENT_ERROR_ATTEMPTS: u32 = 10;

/// Why a publish did not reach the broker.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PublishError {
    /// The readings could not be turned into JSON, e.g. a non-finite value.
    Payload,
    /// The event loop rejected the request, e.g. it is shutting down.
    Request,
    /// The request channel stayed full for [`PUBLISH_TIMEOUT`].
    Timeout,
}

pub struct MqttHandler {
    client: AsyncClient,
    prefix: String,
    metrics: Arc<MqttMetrics>,
}

/// The rumqttc event loop, which connects, reconnects and sends what
/// [`MqttHandler`] queues.
pub struct MqttConnection {
    event_loop: EventLoop,
    broker: String,
    metrics: Arc<MqttMetrics>,
}

impl MqttHandler {
    /// Build the client; nothing is sent until [`MqttConnection::run`] drives it.
    ///
    /// This is the MQTT 3.1.1 client: unlike rumqttc's MQTT 5 client, it bounds
    /// every socket flush by the connection timeout, so a broker that stops
    /// reading surfaces as an error instead of a silent hang
    /// (bytebeamio/rumqtt#1078).
    ///
    /// `credentials` holds a username and password only when both are configured;
    /// otherwise the client connects anonymously.
    pub fn new(
        host: &str,
        port: u16,
        client_id: &str,
        prefix: &str,
        credentials: Option<(&str, &str)>,
    ) -> (Self, MqttConnection) {
        let mut options = MqttOptions::new(client_id, host, port);
        options.set_keep_alive(KEEP_ALIVE);
        options.set_max_packet_size(MAX_PACKET_SIZE, MAX_PACKET_SIZE);
        // This client only publishes, so ask the broker to keep no session for it.
        options.set_clean_session(true);
        if let Some((username, password)) = credentials {
            options.set_credentials(username, password);
        }

        let metrics = MqttMetrics::new();
        let (client, mut event_loop) = AsyncClient::new(options, REQUEST_CHANNEL_CAPACITY);
        let mut network = event_loop.network_options();
        network.set_tcp_send_buffer_size(SEND_BUFFER_SIZE);
        event_loop.set_network_options(network);
        let handler = Self {
            client,
            prefix: prefix.to_string(),
            metrics: metrics.clone(),
        };
        let connection = MqttConnection {
            event_loop,
            broker: format!("{host}:{port}"),
            metrics,
        };
        (handler, connection)
    }

    /// Counters for the shared connection, so the watchdog can report on them.
    pub fn metrics(&self) -> Arc<MqttMetrics> {
        self.metrics.clone()
    }

    /// Publish one parsed packet as a JSON object on `<prefix>/<channel>`.
    ///
    /// The publish is bounded by [`PUBLISH_TIMEOUT`]; if the event loop does not
    /// accept it in time the packet is dropped and reported instead of blocking
    /// the caller, and with it the UDP reader.
    pub async fn publish(
        &self,
        channel: &str,
        variables: &[Variable<'_>],
        topic_map: &TopicMap,
    ) -> Result<(), PublishError> {
        let topic = format!("{}/{}", self.prefix, channel);

        let payload = match packet_payload(variables, topic_map) {
            Ok(payload) => payload,
            Err(e) => {
                self.metrics.incr_publish_errors();
                error!("failed to build payload for '{}': {}", topic, e);
                return Err(PublishError::Payload);
            }
        };
        let payload = match serde_json::to_string(&payload) {
            Ok(payload) => payload,
            Err(e) => {
                self.metrics.incr_publish_errors();
                error!("failed to serialize payload for '{}': {}", topic, e);
                return Err(PublishError::Payload);
            }
        };
        let payload_len = payload.len();

        match tokio::time::timeout(
            PUBLISH_TIMEOUT,
            self.client
                .publish(topic.as_str(), QoS::AtLeastOnce, false, payload),
        )
        .await
        {
            Ok(Ok(())) => {
                self.metrics.incr_enqueued();
                debug!("enqueued {} bytes to '{}'", payload_len, topic);
                Ok(())
            }
            Ok(Err(e)) => {
                self.metrics.incr_publish_errors();
                error!("failed to publish to '{}': {}", topic, e);
                Err(PublishError::Request)
            }
            Err(_elapsed) => {
                let timeouts = self.metrics.incr_publish_timeouts();
                // Throttled: while the broker is stalled this fires once per
                // packet, which would be ten lines a second for the whole outage.
                if should_log_repeated(timeouts) {
                    warn!(
                        "publish to '{}' timed out after {:?}: broker not acknowledging, \
                         dropping packet ({} timeouts so far)",
                        topic, PUBLISH_TIMEOUT, timeouts
                    );
                }
                Err(PublishError::Timeout)
            }
        }
    }
}

impl MqttConnection {
    /// Keep the connection up, reporting it in `readiness`; ready means connected.
    ///
    /// rumqttc reconnects on the next poll after an error; this loop only adds
    /// a backoff capped at [`MAX_BACKOFF`]. Returns, after writing the
    /// termination message, once [`PERMANENT_ERROR_ATTEMPTS`] refusals in a row
    /// show the broker will not accept this client, or once every publisher is gone.
    pub async fn run(mut self, readiness: Readiness) {
        let mut backoff = INITIAL_BACKOFF;
        let mut refusals = 0;
        loop {
            match self.event_loop.poll().await {
                Ok(Event::Incoming(Incoming::ConnAck(_))) => {
                    self.metrics.incr_connects();
                    info!("MQTT connected to {}", self.broker);
                    readiness.ready("mqtt connected");
                    backoff = INITIAL_BACKOFF;
                    refusals = 0;
                }
                Ok(Event::Incoming(Incoming::PubAck(_))) => {
                    self.metrics.incr_acked();
                }
                // rumqttc reconnects on the next poll, as after an error.
                Ok(Event::Incoming(Incoming::Disconnect)) => {
                    warn!("MQTT broker {} disconnected this client", self.broker);
                    readiness.not_ready("mqtt: disconnected by the broker");
                }
                Ok(_) => {}
                Err(ConnectionError::RequestsDone) => {
                    error!("MQTT event loop stopped: every publisher is gone");
                    return;
                }
                Err(e) => {
                    readiness.not_ready(format!("mqtt: {e}"));
                    if is_permanent(&e) {
                        refusals += 1;
                        if refusals >= PERMANENT_ERROR_ATTEMPTS {
                            let message = format!("mqtt: giving up after {refusals} refusals: {e}");
                            error!("{message}");
                            write_termination_message(&message);
                            return;
                        }
                    } else {
                        refusals = 0;
                    }
                    let attempt = self.metrics.incr_reconnects();
                    warn!(
                        "MQTT connection error (attempt {}): {} - reconnecting in {:?}",
                        attempt, e, backoff
                    );
                    tokio::time::sleep(backoff).await;
                    backoff = (backoff * 2).min(MAX_BACKOFF);
                }
            }
        }
    }
}

/// A refusal that retrying is unlikely to fix: bad credentials, client id or protocol.
fn is_permanent(error: &ConnectionError) -> bool {
    matches!(
        error,
        ConnectionError::ConnectionRefused(code) if *code != ConnectReturnCode::ServiceUnavailable
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::{Path, PathBuf};
    use tokio::io::{AsyncReadExt, AsyncWriteExt};
    use tokio::net::{TcpListener, TcpSocket};

    /// CONNACK packets (MQTT 3.1.1): no session, then the return code.
    const CONNACK_NOT_AUTHORIZED: [u8; 4] = [0x20, 0x02, 0x00, 0x05];
    const CONNACK_ACCEPTED: [u8; 4] = [0x20, 0x02, 0x00, 0x00];

    /// A production-sized payload.
    const PAYLOAD_SIZE: usize = 16 * 1024;

    /// Accept one connection per reply: read its CONNECT, answer, then keep it
    /// open without reading anything more.
    fn broker(listener: TcpListener, replies: Vec<[u8; 4]>) -> tokio::task::JoinHandle<()> {
        tokio::spawn(async move {
            let mut open = Vec::new();
            for reply in replies {
                let (mut socket, _) = listener.accept().await.unwrap();
                let mut connect = [0u8; 256];
                let _ = socket.read(&mut connect).await.unwrap();
                socket.write_all(&reply).await.unwrap();
                open.push(socket);
            }
            std::future::pending::<()>().await;
        })
    }

    /// A listener whose connections buffer little, so a client writing to one
    /// that is not read blocks after a few publishes.
    fn small_buffer_listener() -> TcpListener {
        let socket = TcpSocket::new_v4().unwrap();
        socket.set_recv_buffer_size(4096).unwrap();
        socket.bind("127.0.0.1:0".parse().unwrap()).unwrap();
        socket.listen(1).unwrap()
    }

    fn status_file(name: &str) -> PathBuf {
        std::env::temp_dir().join(format!("fiber-optics-{name}-{}", std::process::id()))
    }

    async fn wait_for_status(path: &Path, prefix: &str, limit: Duration) -> String {
        let started = std::time::Instant::now();
        while started.elapsed() < limit {
            let status = std::fs::read_to_string(path).unwrap_or_default();
            if status.starts_with(prefix) {
                return status;
            }
            tokio::time::sleep(Duration::from_millis(50)).await;
        }
        panic!("status never started with {prefix:?} within {limit:?}");
    }

    #[tokio::test]
    async fn readiness_follows_refusal_then_connection() {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let port = listener.local_addr().unwrap().port();
        let server = broker(listener, vec![CONNACK_NOT_AUTHORIZED, CONNACK_ACCEPTED]);
        let path = status_file("refusal");
        let readiness = Readiness::new(&path, "mqtt: connecting");
        let (_handler, connection) = MqttHandler::new("127.0.0.1", port, "test", "fiber", None);
        let running = tokio::spawn(connection.run(readiness));

        let limit = Duration::from_secs(5);
        let refused = wait_for_status(&path, "not ready: mqtt: Connection refused", limit).await;
        assert!(refused.contains("NotAuthorized"));
        wait_for_status(&path, "ready: mqtt connected", limit).await;

        running.abort();
        server.abort();
    }

    /// The 2026-10-13 outage: the broker's pod vanished without a reset, so the
    /// client's writes stopped draining. The MQTT 5 client hung on its flush.
    #[tokio::test]
    async fn not_ready_soon_after_the_broker_stops_reading() {
        let listener = small_buffer_listener();
        let port = listener.local_addr().unwrap().port();
        let server = broker(listener, vec![CONNACK_ACCEPTED]);
        let path = status_file("stalled");
        let readiness = Readiness::new(&path, "mqtt: connecting");
        let (handler, connection) = MqttHandler::new("127.0.0.1", port, "test", "fiber", None);
        let running = tokio::spawn(connection.run(readiness));
        wait_for_status(&path, "ready: mqtt connected", Duration::from_secs(5)).await;

        let publishing = tokio::spawn(async move {
            let payload = "x".repeat(PAYLOAD_SIZE);
            loop {
                let publish =
                    handler
                        .client
                        .publish("fiber/test", QoS::AtLeastOnce, false, payload.clone());
                let _ = tokio::time::timeout(PUBLISH_TIMEOUT, publish).await;
            }
        });

        let stalled = wait_for_status(&path, "not ready: mqtt:", Duration::from_secs(15)).await;
        assert!(stalled.contains("Flush timeout"), "{stalled}");

        publishing.abort();
        running.abort();
        server.abort();
    }

    #[test]
    fn refusals_other_than_unavailable_are_permanent() {
        let refused = ConnectionError::ConnectionRefused;
        assert!(is_permanent(&refused(
            ConnectReturnCode::BadUserNamePassword
        )));
        assert!(is_permanent(&refused(ConnectReturnCode::NotAuthorized)));
        assert!(!is_permanent(&refused(
            ConnectReturnCode::ServiceUnavailable
        )));
        assert!(!is_permanent(&ConnectionError::NetworkTimeout));
    }
}
