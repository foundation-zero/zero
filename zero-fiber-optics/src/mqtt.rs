use crate::layout::{topic_segment, TopicMap, Variable, VariableValue};
use rumqttc::{AsyncClient, MqttOptions, QoS};
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
        if let (Some(user), Some(pass)) = (username, password) {
            mqttoptions.set_credentials(user, pass);
        }

        let (client, mut eventloop) = AsyncClient::new(mqttoptions, 10);

        // Spawn a task to handle the event loop
        tokio::spawn(async move {
            while let Ok(_) = eventloop.poll().await {
                // Keep the connection alive
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
        for var in variables {
            let seg = topic_segment(topic_map, var.key);
            let topic = format!("{}/{}/{}", self.prefix, channel, seg);
            let payload = match &var.value {
                VariableValue::Number(v) => v.to_string(),
                VariableValue::Boolean(v) => v.to_string(),
            };

            self.client
                .publish(topic, QoS::AtLeastOnce, false, payload)
                .await?;
        }
        Ok(())
    }
}
