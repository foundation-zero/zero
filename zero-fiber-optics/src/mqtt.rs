use crate::layout::{packet_payload, TopicMap, Variable};
use log::{error, info, warn};
use rumqttc::{AsyncClient, ConnectionError, Event, Incoming, MqttOptions, Outgoing, QoS};
use std::time::Duration;
use tokio_retry::strategy::{jitter, ExponentialBackoff};

pub struct MqttHandler {
    client: AsyncClient,
    prefix: String,
}

impl MqttHandler {
    pub async fn new(
        host: &str,
        port: u16,
        client_id: &str,
        prefix: &str,
        username: Option<&str>,
        password: Option<&str>,
    ) -> anyhow::Result<Self> {
        let mut mqttoptions = MqttOptions::new(client_id, host, port);
        mqttoptions.set_keep_alive(Duration::from_secs(5));
        mqttoptions.set_max_packet_size(65536, 65536);
        if let (Some(user), Some(pass)) = (username, password) {
            mqttoptions.set_credentials(user, pass);
        }

        let (client, mut eventloop) = AsyncClient::new(mqttoptions, 10);
        let host_for_log = host.to_string();
        let username_for_log = username.unwrap_or("<none>").to_string();

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
                    Ok(Event::Incoming(Incoming::ConnAck(_))) => {
                        info!(
                            "MQTT client connected to {}:{} as username '{}'",
                            host_for_log, port, username_for_log
                        );
                        backoff = make_backoff();
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
                        warn!(
                            "MQTT connection error: {} — reconnecting in {:?}",
                            e, delay
                        );
                        tokio::time::sleep(delay).await;
                    }
                }
            }
        });

        Ok(Self {
            client,
            prefix: prefix.to_string(),
        })
    }

    pub async fn publish(
        &self,
        channel: &str,
        variables: &[Variable<'_>],
        topic_map: &TopicMap,
    ) -> anyhow::Result<()> {
        let topic = format!("{}/{}", self.prefix, channel);
        let payload = serde_json::to_string(&packet_payload(variables, topic_map)?)?;

        self.client
            .publish(topic.clone(), QoS::AtLeastOnce, false, payload)
            .await
            .map_err(|e| anyhow::anyhow!("Failed to publish to topic '{}': {}", topic, e))?;
        Ok(())
    }
}
