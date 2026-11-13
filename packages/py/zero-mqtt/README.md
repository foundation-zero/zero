# zero-mqtt

A FastStream MQTT broker that rides out broker outages, and its readiness
check for [zero-health](../zero-health), following
[ADR 0001](../../../docs/adr/0001-dependency-outages.md).

```python
broker = MqttSettings().make_broker()
health = Health(HealthSettings(), {"mqtt": broker_check(broker)})
async with health.serve():
    await FastStream(broker).run()
```

The broker reconnects for as long as it takes, at most 30 s apart, with a 15 s
keepalive. When the client gives up anyway, the process exits with the reason
as its termination message. Until ZERO-2532 it also retries CONNACK refusals,
which RabbitMQ sends for about a minute after it boots, and exits when they
last longer than 90 s.

`broker_check` is ready while the broker answers a ping within
`HEALTH_CHECK_TIMEOUT`.

| Variable | Default |
|---|---|
| `MQTT_HOST` | required |
| `MQTT_PORT` | required |
| `MQTT_USERNAME` | none |
| `MQTT_PASSWORD` | none |
| `MQTT_CLIENT_ID` | `zero-` and 8 random hex digits |

A service with a second broker subclasses `MqttSettings` with an `env_prefix`
and passes `make_broker(name=...)` a name for its logs and exits.

## Development

```sh
just check
```
