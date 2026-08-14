use crate::layout::{packet_payload, TopicMap, Variable};
use log::{error, info, warn};
use rumqttc::{AsyncClient, Event, Incoming, MqttOptions, Outgoing, QoS};
use std::time::Duration;

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

        // Spawn a task to handle the event loop
        tokio::spawn(async move {
            loop {
                match eventloop.poll().await {
                    Ok(Event::Incoming(Incoming::ConnAck(_))) => {
                        info!(
                            "MQTT client connected to {}:{} as username '{}'",
                            host_for_log, port, username_for_log
                        );
                    }
                    Ok(Event::Outgoing(Outgoing::Disconnect)) => {
                        warn!("MQTT client disconnected");
                    }
                    Ok(_) => {
                        // Keep the connection alive
                    }
                    Err(e) => {
                        error!("MQTT event loop stopped: {}", e);
                        break;
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
