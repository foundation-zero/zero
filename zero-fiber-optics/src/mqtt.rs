use crate::layout::{packet_payload, TopicMap, Variable};
use crate::metrics::{should_log_repeated, MqttMetrics};
use log::{debug, error, info, warn};
use rumqttc::v5::mqttbytes::v5::{ConnectProperties, ConnectReturnCode, PubAckReason};
use rumqttc::v5::mqttbytes::QoS;
use rumqttc::v5::{AsyncClient, ConnectionError, Event, Incoming, MqttOptions};
use rumqttc::Outgoing;
use std::sync::Arc;
use std::time::Duration;
use tokio_retry::strategy::{jitter, ExponentialBackoff};

/// Keep-alive interval. The MQTT 5 client options require at least 5 seconds.
const KEEP_ALIVE: Duration = Duration::from_secs(5);

/// Largest accepted packet size. A production payload (390 readings) is roughly
/// 16 KB of JSON.
const MAX_PACKET_SIZE: u32 = 65536;

/// Capacity of the channel between publishers and the event loop.
const REQUEST_CHANNEL_CAPACITY: usize = 10;

/// How long a publish may wait for room in the request channel before it is
/// abandoned.
///
/// A healthy enqueue takes microseconds, so reaching this means the event loop
/// is not draining requests - a stalled or blocked broker. Bounding it is what
/// keeps that from wedging the UDP reader waiting behind it.
const PUBLISH_TIMEOUT: Duration = Duration::from_secs(5);

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

impl MqttHandler {
    /// Connect to the broker and start polling the event loop in the background.
    ///
    /// `credentials` holds a username and password only when both are configured;
    /// otherwise the client connects anonymously.
    pub async fn new(
        host: &str,
        port: u16,
        client_id: &str,
        prefix: &str,
        credentials: Option<(&str, &str)>,
    ) -> anyhow::Result<Self> {
        let mut mqttoptions = MqttOptions::new(client_id, host, port);
        mqttoptions.set_keep_alive(KEEP_ALIVE);

        let mut connect_properties = ConnectProperties::new();
        // This client only publishes, so ask the broker to retain no session
        // state for it. That also sidesteps the broker's session retention
        // window, which RabbitMQ defaults to 24 hours.
        connect_properties.session_expiry_interval = Some(0);
        connect_properties.max_packet_size = Some(MAX_PACKET_SIZE);
        mqttoptions.set_connect_properties(connect_properties);

        if let Some((username, password)) = credentials {
            mqttoptions.set_credentials(username, password);
        }

        let metrics = MqttMetrics::new();
        let (client, mut eventloop) = AsyncClient::new(mqttoptions, REQUEST_CHANNEL_CAPACITY);
        let host_for_log = host.to_string();
        let metrics_for_loop = metrics.clone();

        tokio::spawn(async move {
            let make_backoff = || {
                ExponentialBackoff::from_millis(2)
                    .factor(500)
                    .max_delay(Duration::from_secs(60))
                    .map(jitter)
            };
            let mut backoff = make_backoff();

            loop {
                match eventloop.poll().await {
                    Ok(Event::Incoming(Incoming::ConnAck(ack))) => {
                        metrics_for_loop.incr_connects();
                        if ack.code == ConnectReturnCode::Success {
                            info!(
                                "MQTT 5 connected to {}:{} (reason={:?}, session_present={})",
                                host_for_log, port, ack.code, ack.session_present
                            );
                            backoff = make_backoff();
                        } else {
                            error!(
                                "MQTT 5 connection to {}:{} refused by broker: reason={:?}",
                                host_for_log, port, ack.code
                            );
                        }
                    }
                    Ok(Event::Incoming(Incoming::PubAck(ack))) => {
                        // NoMatchingSubscribers is the broker accepting the message
                        // with nothing subscribed to the topic, not a rejection.
                        if matches!(
                            ack.reason,
                            PubAckReason::Success | PubAckReason::NoMatchingSubscribers
                        ) {
                            metrics_for_loop.incr_acked();
                        } else {
                            metrics_for_loop.incr_puback_denied();
                            warn!(
                                "broker rejected publish {}: reason={:?}",
                                ack.pkid, ack.reason
                            );
                        }
                    }
                    Ok(Event::Incoming(Incoming::Disconnect(disconnect))) => {
                        metrics_for_loop.incr_server_disconnects();
                        warn!(
                            "broker closed the connection: reason={:?}",
                            disconnect.reason_code
                        );
                    }
                    Ok(Event::Outgoing(Outgoing::Disconnect)) => {
                        warn!("MQTT client disconnected");
                    }
                    Ok(_) => {}
                    Err(e) => {
                        if matches!(e, ConnectionError::RequestsDone) {
                            error!("MQTT event loop stopped: request channel closed: {}", e);
                            break;
                        }
                        let delay = backoff.next().unwrap_or(Duration::from_secs(60));
                        let attempt = metrics_for_loop.incr_reconnects();
                        warn!(
                            "MQTT connection error (attempt {}): {} - reconnecting in {:?}",
                            attempt, e, delay
                        );
                        tokio::time::sleep(delay).await;
                    }
                }
            }
        });

        Ok(Self {
            client,
            prefix: prefix.to_string(),
            metrics,
        })
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
