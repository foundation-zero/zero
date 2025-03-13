DROP TABLE IF EXISTS rooms CASCADE;

CREATE TABLE
  rooms (
    id TEXT,
    time TIMESTAMPTZ as proctime (),
    actual_temperature REAL,
    temperature_setpoint REAL,
    actual_humidity REAL,
    thermal_comfort_index REAL,
    last_movement TIMESTAMPTZ,
    amplifier_on BOOLEAN,
  )
WITH
  (
    connector = 'mqtt',
    url = 'tcp://mosquitto',
    topic = 'domestic/rooms',
    qos = 'at_least_once',
  ) FORMAT PLAIN ENCODE JSON;

DROP MATERIALIZED VIEW IF EXISTS rooms_collected_status;

CREATE MATERIALIZED VIEW rooms_collected_status AS
SELECT DISTINCT
  id,
  first_value (actual_temperature) OVER (
    partition by
      id
    order BY
      case
        when actual_temperature is not null then time
      end desc nulls last
  ) actual_temperature,
  first_value (temperature_setpoint) OVER (
    partition by
      id
    order BY
      case
        when temperature_setpoint is not null then time
      end desc nulls last
  ) temperature_setpoint,
  first_value (actual_humidity) OVER (
    partition by
      id
    order BY
      case
        when actual_humidity is not null then time
      end desc nulls last
  ) actual_humidity,
  10 thermal_comfort_index,
  first_value (last_movement) OVER (
    partition by
      id
    order BY
      case
        when last_movement is not null then time
      end desc nulls last
  ) last_movement,
  first_value (amplifier_on) OVER (
    partition by
      id
    order by
      case
        when amplifier_on is not null then time
      end desc nulls last
  ) amplifier_on
FROM
  rooms;

DROP SINK IF EXISTS rooms_pg_sink CASCADE;

CREATE SINK rooms_pg_sink
FROM
  rooms_collected_status
WITH
  (
    connector = 'jdbc',
    jdbc.url = 'jdbc:postgresql://postgres:5432/domestic_control?user=postgres&password=postgrespassword',
    table.name = 'rooms',
    type = 'upsert',
    primary_key = 'id'
  );

DROP TABLE IF EXISTS blinds CASCADE;

CREATE TABLE
  blinds (
    id TEXT PRIMARY KEY,
    time TIMESTAMPTZ as proctime (),
    level REAL
  )
WITH
  (
    connector = 'mqtt',
    url = 'tcp://mosquitto',
    topic = 'domestic/blinds',
    qos = 'at_least_once',
  ) FORMAT PLAIN ENCODE JSON;

DROP SINK IF EXISTS blinds_pg_sink CASCADE;

CREATE SINK blinds_pg_sink AS (
  SELECT
    id,
    level
  FROM
    blinds
)
WITH
  (
    connector = 'jdbc',
    jdbc.url = 'jdbc:postgresql://postgres:5432/domestic_control?user=postgres&password=postgrespassword',
    table.name = 'blinds',
    type = 'upsert',
    primary_key = 'id'
  );

DROP TABLE IF EXISTS lighting_groups CASCADE;

CREATE TABLE
  lighting_groups (
    id TEXT PRIMARY KEY,
    time TIMESTAMPTZ as proctime (),
    level REAL
  )
WITH
  (
    connector = 'mqtt',
    url = 'tcp://mosquitto',
    topic = 'domestic/lighting-groups',
    qos = 'at_least_once',
  ) FORMAT PLAIN ENCODE JSON;

DROP SINK IF EXISTS lighting_groups_pg_sink CASCADE;

CREATE SINK lighting_groups_pg_sink AS (
  SELECT
    id,
    level
  FROM
    lighting_groups
)
WITH
  (
    connector = 'jdbc',
    jdbc.url = 'jdbc:postgresql://postgres:5432/domestic_control?user=postgres&password=postgrespassword',
    table.name = 'lighting_groups',
    type = 'upsert',
    primary_key = 'id'
  );