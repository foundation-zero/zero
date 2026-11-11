use crate::cells::ModuleFrame;
use crate::config::AppConfig;
use log::{error, info, warn};
use rumqttc::{
    AsyncClient, ConnectReturnCode, ConnectionError, Event, EventLoop, Incoming, MqttOptions, QoS,
};
use std::time::Duration;
use tokio::time::timeout;
use zero_readiness::{write_termination_message, Readiness};

/// MQTT keep-alive interval: how quickly a dead connection is noticed.
const KEEP_ALIVE: Duration = Duration::from_secs(15);

/// Capacity of the channel between publishers and the event loop.
const REQUEST_CHANNEL_CAPACITY: usize = 10;

/// How long a publish may wait for room in the request channel before it is
/// abandoned and dropped.
///
/// A healthy enqueue takes microseconds; landing on this means the event loop
/// is not draining requests, usually a stalled broker. Bounding it keeps the
/// decoder from piling up behind a stuck publisher.
const PUBLISH_TIMEOUT: Duration = Duration::from_secs(5);

/// First reconnect delay before the event loop backs off.
const INITIAL_BACKOFF: Duration = Duration::from_secs(1);
/// Reconnect delay ceiling: the client reconnects within this long after the broker is back.
const MAX_BACKOFF: Duration = Duration::from_secs(30);

/// Refusals such as bad credentials before giving up, in about 3 minutes of
/// backoff. A booting broker can refuse logins too, so the first is not final.
const PERMANENT_ERROR_ATTEMPTS: u32 = 10;

/// Why a message did not reach the broker.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PublishError {
    /// The event loop rejected the request, e.g. it is shutting down.
    Request,
    /// The request channel stayed full for [`PUBLISH_TIMEOUT`].
    Timeout,
    /// The frame could not be serialised to JSON.
    Encode,
}

/// Terminal condition: the MQTT leg of the pipeline has stopped delivering.
///
/// Raised when the frame queue closes (the publish task ended) or when the
/// MQTT client stops handing requests to its event loop.
#[derive(Debug)]
pub struct MqttGone;

impl std::fmt::Display for MqttGone {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(formatter, "MQTT stopped delivering")
    }
}

/// Thin wrapper around a rumqttc client, publishing module frames.
pub struct MqttPublisher {
    client: AsyncClient,
    /// First topic segment, see [`ModuleFrame::topic`].
    prefix: String,
}

/// The rumqttc event loop, which connects, reconnects and sends what
/// [`MqttPublisher`] queues.
pub struct MqttConnection {
    event_loop: EventLoop,
    host: String,
}

impl MqttPublisher {
    /// Build the client; nothing is sent until [`MqttConnection::run`] drives it.
    pub fn new(app: &AppConfig, client_id: &str) -> (Self, MqttConnection) {
        let mut options = MqttOptions::new(client_id, &app.mqtt_host, app.mqtt_port);
        options.set_keep_alive(KEEP_ALIVE);
        if let Some((username, password)) = app.credentials() {
            options.set_credentials(username, password);
        }

        let (client, event_loop) = AsyncClient::new(options, REQUEST_CHANNEL_CAPACITY);
        let publisher = Self {
            client,
            prefix: app.mqtt_prefix.clone(),
        };
        let connection = MqttConnection {
            event_loop,
            host: app.mqtt_host.clone(),
        };
        (publisher, connection)
    }

    /// Publish one module frame on its topic.
    ///
    /// The topic and JSON payload are built here, directly into the buffers
    /// rumqttc takes ownership of: those two allocations per publish are the
    /// floor its API allows.
    ///
    /// The wait for the event loop is bounded by [`PUBLISH_TIMEOUT`]; on
    /// timeout the message is dropped instead of blocking the decoder.
    pub async fn publish(&self, frame: &ModuleFrame<'_>) -> Result<(), PublishError> {
        let payload = serde_json::to_vec(frame).map_err(|e| {
            error!("Failed to serialise '{}': {}", frame.topic(&self.prefix), e);
            PublishError::Encode
        })?;
        match timeout(
            PUBLISH_TIMEOUT,
            self.client
                .publish(frame.topic(&self.prefix), QoS::AtLeastOnce, false, payload),
        )
        .await
        {
            Ok(Ok(())) => Ok(()),
            Ok(Err(e)) => {
                error!(
                    "MQTT rejected publish to '{}': {}",
                    frame.topic(&self.prefix),
                    e
                );
                Err(PublishError::Request)
            }
            Err(_elapsed) => Err(PublishError::Timeout),
        }
    }
}

impl MqttConnection {
    /// Keep the connection up, reporting it in `readiness`; ready means connected.
    ///
    /// rumqttc reconnects on the next poll after an error; this loop only adds
    /// a backoff capped at [`MAX_BACKOFF`]. Returns, after writing the
    /// termination message, once [`PERMANENT_ERROR_ATTEMPTS`] refusals in a row
    /// show the broker will not accept this client.
    pub async fn run(mut self, readiness: Readiness) {
        let mut backoff = INITIAL_BACKOFF;
        let mut refusals = 0;
        loop {
            match self.event_loop.poll().await {
                Ok(Event::Incoming(Incoming::ConnAck(_))) => {
                    info!("MQTT connected to {}", self.host);
                    readiness.ready("mqtt connected");
                    backoff = INITIAL_BACKOFF;
                    refusals = 0;
                }
                // rumqttc reconnects on the next poll, as after an error.
                Ok(Event::Incoming(Incoming::Disconnect)) => {
                    warn!("MQTT broker {} disconnected this client", self.host);
                    readiness.not_ready("mqtt: disconnected by the broker");
                }
                Ok(_) => {}
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
                    warn!("MQTT connection error: {}. Retrying in {:?}...", e, backoff);
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
    use tokio::io::{AsyncReadExt, AsyncWriteExt};
    use tokio::net::TcpListener;

    /// CONNACK packets (MQTT 3.1.1): no session, then the return code.
    const CONNACK_NOT_AUTHORIZED: [u8; 4] = [0x20, 0x02, 0x00, 0x05];
    const CONNACK_ACCEPTED: [u8; 4] = [0x20, 0x02, 0x00, 0x00];

    /// Accept one connection per reply: read its CONNECT, answer, keep it open.
    async fn broker(replies: Vec<[u8; 4]>) -> (u16, tokio::task::JoinHandle<()>) {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let port = listener.local_addr().unwrap().port();
        let server = tokio::spawn(async move {
            let mut open = Vec::new();
            for reply in replies {
                let (mut socket, _) = listener.accept().await.unwrap();
                let mut connect = [0u8; 256];
                let _ = socket.read(&mut connect).await.unwrap();
                socket.write_all(&reply).await.unwrap();
                open.push(socket);
            }
            std::future::pending::<()>().await;
        });
        (port, server)
    }

    async fn wait_for_status(path: &std::path::Path, prefix: &str) -> String {
        for _ in 0..100 {
            let status = std::fs::read_to_string(path).unwrap_or_default();
            if status.starts_with(prefix) {
                return status;
            }
            tokio::time::sleep(Duration::from_millis(50)).await;
        }
        panic!("status never started with {prefix:?}");
    }

    #[tokio::test]
    async fn readiness_follows_refusal_then_connection() {
        let (port, server) = broker(vec![CONNACK_NOT_AUTHORIZED, CONNACK_ACCEPTED]).await;
        let app = AppConfig {
            mqtt_host: "127.0.0.1".to_string(),
            mqtt_port: port,
            mqtt_prefix: "battery".to_string(),
            udp_port: 0,
            mqtt_username: None,
            mqtt_password: None,
        };
        let path = std::env::temp_dir().join(format!("mqtt-ready-{}", std::process::id()));
        let readiness = Readiness::new(&path, "mqtt: connecting");
        let (_publisher, connection) = MqttPublisher::new(&app, "test");
        let running = tokio::spawn(connection.run(readiness));

        let refused = wait_for_status(&path, "not ready: mqtt: Connection refused").await;
        assert!(refused.contains("NotAuthorized"));
        wait_for_status(&path, "ready: mqtt connected").await;

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
