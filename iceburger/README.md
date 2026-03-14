# Iceburger

A Python application which reads JSON messages from RabbitMQ, batches them and stores them in Iceberg. The schema is automatically derived from the messages. Delivery is at least once.

It can be configured to combine multiple routing keys into one table. Any messages unmatched will automatically be allocated to a table named after the routing key.

Iceburger tries to evolve the schema, if there is a change. If it can't it will drop the messages.

## Settings

Settings can be provided by env variables or a .env:

```
RABBITMQ_HOST
RABBITMQ_PORT
RABBITMQ_USERNAME
RABBITMQ_PASSWORD
ICEBERG_CATALOG_TYPE
ICEBERG_CATALOG_URI
ICEBERG_WAREHOUSE
S3_ENDPOINT
S3_ACCESS_KEY_ID
S3_SECRET_ACCESS_KEY
SINK_WORKERS
CONFIG_PATH
```

## Config

Configuration is done by a YAML:

```yaml
batch:
  size: 10_000
  seconds: 300
amqp: # RabbitMQ config
  exchange: amq.topic # Exchange which to bind
  queue: mqtt.messages # Name of the queue
  routing_keys: ["#"] # Routing keys to bind to the queue
routings: # Routing keys to combine
  - routing_key_prefix: a # Messages with routing keys start with with "a" get combined
    table: as # Stored in table "as"
    timestamp: true # And the RabbitMQ timestamp is included in the table
    exclude_routing_key: true # The routing key of the message isn't included in the table (default false)
```
