use crate::cells::ModuleFrame;
use crate::config::AppConfig;
use anyhow::Result;
use log::{error, info, warn};
use rumqttc::{AsyncClient, Event, Incoming, MqttOptions, QoS};
use std::time::Duration;
use tokio::time::timeout;

/// MQTT keep-alive interval.
const KEEP_ALIVE: Duration = Duration::from_secs(5);

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
/// Reconnect delay ceiling.
const MAX_BACKOFF: Duration = Duration::from_secs(60);

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

impl MqttPublisher {
    /// Build the client and drive its event loop in a background task.
    ///
    /// rumqttc reconnects internally; the loop only resets a backoff that never
    /// grows past [`MAX_BACKOFF`].
    pub async fn new(app: &AppConfig, client_id: &str) -> Result<Self> {
        let mut options = MqttOptions::new(client_id, &app.mqtt_host, app.mqtt_port);
        options.set_keep_alive(KEEP_ALIVE);
        if let Some((username, password)) = app.credentials() {
            options.set_credentials(username, password);
        }

        let (client, mut event_loop) = AsyncClient::new(options, REQUEST_CHANNEL_CAPACITY);
        let host = app.mqtt_host.clone();
        let mut backoff = INITIAL_BACKOFF;

        tokio::spawn(async move {
            loop {
                match event_loop.poll().await {
                    Ok(Event::Incoming(Incoming::ConnAck(_))) => {
                        info!("MQTT connected to {}", host);
                        backoff = INITIAL_BACKOFF;
                    }
                    Ok(_) => {}
                    Err(e) => {
                        warn!("MQTT connection error: {}. Retrying in {:?}...", e, backoff);
                        tokio::time::sleep(backoff).await;
                        backoff = (backoff * 2).min(MAX_BACKOFF);
                    }
                }
            }
        });

        Ok(Self {
            client,
            prefix: app.mqtt_prefix.clone(),
        })
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
