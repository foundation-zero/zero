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

INSERT INTO rooms (id, actual_temperature, temperature_setpoint, amplifier_on) VALUES 
('owners-cabin', 22.5, 21.0, true),
('dutch-cabin', 22.5, 21.0, true),
('french-cabin', 22.5, 21.0, true),
('italian-cabin', 22.5, 21.0, true),
('californian-lounge', 22.5, 21.0, true),
('polynesian-cabin', 22.5, 21.0, true),
('galley', 22.5, 21.0, true),
('crew-mess', 22.5, 21.0, true),
('mission-room', 22.5, 21.0, true),
('laundry', 22.5, 21.0, true),
('engineers-office', 22.5, 21.0, true),
('captains-cabin', 22.5, 21.0, true),
('crew-sb-aft-cabin', 22.5, 21.0, true),
('crew-sb-mid-cabin', 22.5, 21.0, true),
('crew-sb-fwd-cabin', 22.5, 21.0, true),
('crew-ps-mid-cabin', 22.5, 21.0, true),
('crew-ps-fwd-cabin', 22.5, 21.0, true),
('owners-deckhouse', 22.5, 21.0, true),
('owners-cockpit', 22.5, 21.0, true),
('main-deckhouse', 22.5, 21.0, true),
('main-cockpit', 22.5, 21.0, true),
('owners-stairway', 22.5, 21.0, true),
('guest-corridor', 22.5, 21.0, true),
('polynesian-corridor', 22.5, 21.0, true);

INSERT INTO blinds (id, level) VALUES 
('owners-cabin/main/shear', 0),
('owners-cabin/main/blind', 0),
('owners-cabin/port/shear', 0),
('owners-cabin/port/blind', 0),
('owners-cabin/starboard/shear', 0),
('owners-cabin/starboard/blind', 0),
('owners-cabin/skyline_main/shear', 0),
('owners-cabin/skyline_main/blind', 0),
('owners-cabin/skyline_port/shear', 0),
('owners-cabin/skyline_port/blind', 0),
('owners-cabin/skyline_starboard/shear', 0),
('owners-cabin/skyline_starboard/blind', 0),
('dutch-cabin/blind', 0),
('french-cabin/blind', 0),
('italian-cabin/blind', 0),
('californian-lounge/blind', 0),
('polynesian-cabin/blind', 0),
('galley/blind', 0),
('crew-mess/blind', 0),
('mission-room/blind', 0),
('laundry/blind', 0),
('engineers-office/blind', 0),
('captains-cabin/blind', 0),
('crew-sb-aft-cabin/blind', 0),
('crew-sb-mid-cabin/blind', 0),
('crew-sb-fwd-cabin/blind', 0),
('crew-ps-mid-cabin/blind', 0),
('crew-ps-fwd-cabin/blind', 0),
('owners-deckhouse/blind', 0),
('owners-deckhouse/shear', 0),
('main-deckhouse/blind', 0),
('main-deckhouse/shear', 0),
('owners-stairway/blind', 0),
('guest-corridor/blind', 0);

INSERT INTO lighting_groups (id, level) VALUES 
('owners-cabin/ambient', 0),
('owners-cabin/mood', 0),
('dutch-cabin/ambient', 0),
('dutch-cabin/mood', 0),
('french-cabin/ambient', 0),
('french-cabin/mood', 0),
('italian-cabin/ambient', 0),
('italian-cabin/mood', 0),
('californian-lounge/ambient', 0),
('californian-lounge/mood', 0),
('polynesian-cabin/ambient', 0),
('polynesian-cabin/mood', 0),
('galley/ambient', 0),
('galley/mood', 0),
('crew-mess/ambient', 0),
('crew-mess/mood', 0),
('mission-room/ambient', 0),
('mission-room/mood', 0),
('laundry/ambient', 0),
('laundry/mood', 0),
('engineers-office/ambient', 0),
('engineers-office/mood', 0),
('captains-cabin/ambient', 0),
('captains-cabin/mood', 0),
('crew-sb-aft-cabin/ambient', 0),
('crew-sb-aft-cabin/mood', 0),
('crew-sb-mid-cabin/ambient', 0),
('crew-sb-mid-cabin/mood', 0),
('crew-sb-fwd-cabin/ambient', 0),
('crew-sb-fwd-cabin/mood', 0),
('crew-ps-mid-cabin/ambient', 0),
('crew-ps-mid-cabin/mood', 0),
('crew-ps-fwd-cabin/ambient', 0),
('crew-ps-fwd-cabin/mood', 0),
('owners-deckhouse/ambient', 0),
('owners-deckhouse/mood', 0),
('main-deckhouse/ambient', 0),
('main-deckhouse/mood', 0),
('owners-stairway/main', 0),
('guest-corridor/main', 0),
('polynesian-corridor/main', 0);
