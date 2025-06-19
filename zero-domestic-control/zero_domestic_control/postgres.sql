DROP TABLE IF EXISTS rooms CASCADE;
CREATE TABLE rooms (
  "id" TEXT PRIMARY KEY,
  "name" TEXT,
  "group" TEXT
);

-- DROP TYPE IF EXISTS control_type CASCADE;
-- CREATE TYPE control_type AS ENUM ('light', 'blind', 'amplifier', 'temperature', 'humidity', 'co2');

DROP TABLE IF EXISTS controls CASCADE;
CREATE TABLE controls (
  "id" TEXT PRIMARY KEY,
  "room_id" VARCHAR REFERENCES rooms("id"),
  "type" TEXT,
  "name" TEXT
);

-- DROP TYPE IF EXISTS sensor_type CASCADE;
-- CREATE TYPE sensor_type AS ENUM ('temperature', 'humidity', 'co2');

DROP TABLE IF EXISTS sensors CASCADE;
CREATE TABLE sensors (
  "id" TEXT PRIMARY KEY,
  "room_id" VARCHAR REFERENCES rooms("id"),
  "type" TEXT,
  "name" TEXT
);

-- DROP TYPE IF EXISTS blinds_opacity CASCADE;
-- CREATE TYPE blinds_opacity AS ENUM ('shear', 'blind');

DROP TABLE IF EXISTS blinds CASCADE;
CREATE TABLE blinds (
  "id" TEXT PRIMARY KEY,
  "room_id" VARCHAR REFERENCES rooms("id"),
  "name" TEXT,
  "opacity" TEXT,
  "group" TEXT
);

DROP TABLE IF EXISTS lighting_groups CASCADE;
CREATE TABLE lighting_groups (
  "id" VARCHAR PRIMARY KEY,
  "room_id" VARCHAR REFERENCES rooms("id"),
  "name" TEXT
);

DROP TABLE IF EXISTS amplifiers CASCADE;
CREATE TABLE amplifiers (
  "id" VARCHAR PRIMARY KEY,
  "room_id" VARCHAR REFERENCES rooms("id"),
  "name" TEXT
);

DROP TABLE IF EXISTS rooms_controls_log CASCADE;
CREATE TABLE rooms_controls_log (
  "id" VARCHAR REFERENCES controls("id"),
  "room_id" VARCHAR REFERENCES rooms("id"),
  "name" TEXT,
  "type" TEXT,
  "value" REAL,
  "time" TIMESTAMPTZ
);

DROP TABLE IF EXISTS rooms_sensors_log CASCADE;
CREATE TABLE rooms_sensors_log (
  "id" VARCHAR REFERENCES controls("id"),
  "room_id" VARCHAR REFERENCES rooms("id"),
  "name" TEXT,
  "type" TEXT,
  "value" REAL,
  "time" TIMESTAMPTZ
);

DROP TABLE IF EXISTS rooms_controls CASCADE;
CREATE TABLE rooms_controls (
  "id" TEXT PRIMARY KEY,
  "room_id" VARCHAR REFERENCES rooms("id"),
  "name" TEXT,
  "type" TEXT,
  "value" TEXT,
  "time" TIMESTAMPTZ
);

DROP TABLE IF EXISTS rooms_sensors CASCADE;
CREATE TABLE rooms_sensors (
  "id" TEXT PRIMARY KEY,
  "room_id" VARCHAR REFERENCES rooms("id"),
  "name" TEXT,
  "type" TEXT,
  "value" TEXT,
  "time" TIMESTAMPTZ
);

INSERT INTO rooms ("id", "name", "group") VALUES
('owners-cabin', 'Owners cabin', 'AFT'),
('dutch-cabin', 'Dutch cabin', 'AFT'),
('french-cabin', 'French cabin', 'AFT'),
('italian-cabin', 'Italian cabin', 'AFT'),
('californian-lounge', 'Californian lounge', 'AFT'),
('polynesian-cabin', 'Polynesian cabin', 'MID'),
('galley', 'Galley', 'MID'),
('crew-mess', 'Crew mess', 'MID'),
('mission-room', 'Mission room', 'MID'),
('laundry', 'Laundry', 'MID'),
('engineers-office', 'Engineers office', 'MID'),
('captains-cabin', 'Captains cabin', 'FORE'),
('crew-sb-aft-cabin', 'Crew SB AFT cabin', 'FORE'),
('crew-sb-mid-cabin', 'Crew SB MID cabin', 'FORE'),
('crew-sb-fwd-cabin', 'Crew SB FWD cabin', 'FORE'),
('crew-ps-mid-cabin', 'Crew PS MID cabin', 'FORE'),
('crew-ps-fwd-cabin', 'Crew PS FWD cabin', 'FORE'),
('owners-deckhouse', 'Owners deckhouse', 'UPPERDECK'),
('owners-cockpit', 'Owners cockpit', 'AFT'),
('main-deckhouse', 'Main deckhouse', 'UPPERDECK'),
('main-cockpit', 'Main cockpit', 'UPPERDECK'),
('owners-stairway', 'Owners stairway', 'HALLWAYS'),
('guest-corridor', 'Guest corridor', 'HALLWAYS'),
('polynesian-corridor', 'Polynesian corridor', 'HALLWAYS');

INSERT INTO controls ("id", "room_id", "type", "name") VALUES
('owners-cabin/control/temperature', 'owners-cabin', 'temperature', ''),
('owners-cabin/control/humidity', 'owners-cabin', 'humidity', ''),
('owners-cabin/control/co2', 'owners-cabin', 'co2', ''),
('dutch-cabin/control/temperature', 'dutch-cabin', 'temperature', ''),
('dutch-cabin/control/humidity', 'dutch-cabin', 'humidity', ''),
('dutch-cabin/control/co2', 'dutch-cabin', 'co2', ''),
('french-cabin/control/temperature', 'french-cabin', 'temperature', ''),
('french-cabin/control/humidity', 'french-cabin', 'humidity', ''),
('french-cabin/control/co2', 'french-cabin', 'co2', ''),
('italian-cabin/control/temperature', 'italian-cabin', 'temperature', ''),
('italian-cabin/control/humidity', 'italian-cabin', 'humidity', ''),
('italian-cabin/control/co2', 'italian-cabin', 'co2', ''),
('californian-lounge/control/temperature', 'californian-lounge', 'temperature', ''),
('californian-lounge/control/humidity', 'californian-lounge', 'humidity', ''),
('californian-lounge/control/co2', 'californian-lounge', 'co2', ''),
('polynesian-cabin/control/temperature', 'polynesian-cabin', 'temperature', ''),
('polynesian-cabin/control/humidity', 'polynesian-cabin', 'humidity', ''),
('polynesian-cabin/control/co2', 'polynesian-cabin', 'co2', ''),
('galley/control/temperature', 'galley', 'temperature', ''),
('galley/control/humidity', 'galley', 'humidity', ''),
('galley/control/co2', 'galley', 'co2', ''),
('crew-mess/control/temperature', 'crew-mess', 'temperature', ''),
('crew-mess/control/humidity', 'crew-mess', 'humidity', ''),
('crew-mess/control/co2', 'crew-mess', 'co2', ''),
('mission-room/control/temperature', 'mission-room', 'temperature', ''),
('mission-room/control/humidity', 'mission-room', 'humidity', ''),
('mission-room/control/co2', 'mission-room', 'co2', ''),
('laundry/control/temperature', 'laundry', 'temperature', ''),
('laundry/control/humidity', 'laundry', 'humidity', ''),
('laundry/control/co2', 'laundry', 'co2', ''),
('engineers-office/control/temperature', 'engineers-office', 'temperature', ''),
('engineers-office/control/humidity', 'engineers-office', 'humidity', ''),
('engineers-office/control/co2', 'engineers-office', 'co2', ''),
('captains-cabin/control/temperature', 'captains-cabin', 'temperature', ''),
('captains-cabin/control/humidity', 'captains-cabin', 'humidity', ''),
('captains-cabin/control/co2', 'captains-cabin', 'co2', ''),
('crew-sb-aft-cabin/control/temperature', 'crew-sb-aft-cabin', 'temperature', ''),
('crew-sb-aft-cabin/control/humidity', 'crew-sb-aft-cabin', 'humidity', ''),
('crew-sb-aft-cabin/control/co2', 'crew-sb-aft-cabin', 'co2', ''),
('crew-sb-mid-cabin/control/temperature', 'crew-sb-mid-cabin', 'temperature', ''),
('crew-sb-mid-cabin/control/humidity', 'crew-sb-mid-cabin', 'humidity', ''),
('crew-sb-mid-cabin/control/co2', 'crew-sb-mid-cabin', 'co2', ''),
('crew-sb-fwd-cabin/control/temperature', 'crew-sb-fwd-cabin', 'temperature', ''),
('crew-sb-fwd-cabin/control/humidity', 'crew-sb-fwd-cabin', 'humidity', ''),
('crew-sb-fwd-cabin/control/co2', 'crew-sb-fwd-cabin', 'co2', ''),
('crew-ps-mid-cabin/control/temperature', 'crew-ps-mid-cabin', 'temperature', ''),
('crew-ps-mid-cabin/control/humidity', 'crew-ps-mid-cabin', 'humidity', ''),
('crew-ps-mid-cabin/control/co2', 'crew-ps-mid-cabin', 'co2', ''),
('crew-ps-fwd-cabin/control/temperature', 'crew-ps-fwd-cabin', 'temperature', ''),
('crew-ps-fwd-cabin/control/humidity', 'crew-ps-fwd-cabin', 'humidity', ''),
('crew-ps-fwd-cabin/control/co2', 'crew-ps-fwd-cabin', 'co2', ''),
('owners-deckhouse/control/temperature', 'owners-deckhouse', 'temperature', ''),
('owners-deckhouse/control/humidity', 'owners-deckhouse', 'humidity', ''),
('owners-deckhouse/control/co2', 'owners-deckhouse', 'co2', ''),
('main-deckhouse/control/temperature', 'main-deckhouse', 'temperature', ''),
('main-deckhouse/control/humidity', 'main-deckhouse', 'humidity', ''),
('main-deckhouse/control/co2', 'main-deckhouse', 'co2', ''),
('owners-stairway/control/temperature', 'owners-stairway', 'temperature', ''),
('owners-stairway/control/humidity', 'owners-stairway', 'humidity', ''),
('owners-stairway/control/co2', 'owners-stairway', 'co2', ''),
('guest-corridor/control/temperature', 'guest-corridor', 'temperature', ''),
('guest-corridor/control/humidity', 'guest-corridor', 'humidity', ''),
('guest-corridor/control/co2', 'guest-corridor', 'co2', ''),
('polynesian-corridor/control/temperature', 'polynesian-corridor', 'temperature', ''),
('polynesian-corridor/control/humidity', 'polynesian-corridor', 'humidity', ''),
('polynesian-corridor/control/co2', 'polynesian-corridor', 'co2', '');


INSERT INTO sensors ("id", "room_id", "type", "name") VALUES
('owners-cabin/sensor/temperature', 'owners-cabin', 'temperature', ''),
('owners-cabin/sensor/humidity', 'owners-cabin', 'humidity', ''),
('owners-cabin/sensor/co2', 'owners-cabin', 'co2', ''),
('dutch-cabin/sensor/temperature', 'dutch-cabin', 'temperature', ''),
('dutch-cabin/sensor/humidity', 'dutch-cabin', 'humidity', ''),
('dutch-cabin/sensor/co2', 'dutch-cabin', 'co2', ''),
('french-cabin/sensor/temperature', 'french-cabin', 'temperature', ''),
('french-cabin/sensor/humidity', 'french-cabin', 'humidity', ''),
('french-cabin/sensor/co2', 'french-cabin', 'co2', ''),
('italian-cabin/sensor/temperature', 'italian-cabin', 'temperature', ''),
('italian-cabin/sensor/humidity', 'italian-cabin', 'humidity', ''),
('italian-cabin/sensor/co2', 'italian-cabin', 'co2', ''),
('californian-lounge/sensor/temperature', 'californian-lounge', 'temperature', ''),
('californian-lounge/sensor/humidity', 'californian-lounge', 'humidity', ''),
('californian-lounge/sensor/co2', 'californian-lounge', 'co2', ''),
('polynesian-cabin/sensor/temperature', 'polynesian-cabin', 'temperature', ''),
('polynesian-cabin/sensor/humidity', 'polynesian-cabin', 'humidity', ''),
('polynesian-cabin/sensor/co2', 'polynesian-cabin', 'co2', ''),
('galley/sensor/temperature', 'galley', 'temperature', ''),
('galley/sensor/humidity', 'galley', 'humidity', ''),
('galley/sensor/co2', 'galley', 'co2', ''),
('crew-mess/sensor/temperature', 'crew-mess', 'temperature', ''),
('crew-mess/sensor/humidity', 'crew-mess', 'humidity', ''),
('crew-mess/sensor/co2', 'crew-mess', 'co2', ''),
('mission-room/sensor/temperature', 'mission-room', 'temperature', ''),
('mission-room/sensor/humidity', 'mission-room', 'humidity', ''),
('mission-room/sensor/co2', 'mission-room', 'co2', ''),
('laundry/sensor/temperature', 'laundry', 'temperature', ''),
('laundry/sensor/humidity', 'laundry', 'humidity', ''),
('laundry/sensor/co2', 'laundry', 'co2', ''),
('engineers-office/sensor/temperature', 'engineers-office', 'temperature', ''),
('engineers-office/sensor/humidity', 'engineers-office', 'humidity', ''),
('engineers-office/sensor/co2', 'engineers-office', 'co2', ''),
('captains-cabin/sensor/temperature', 'captains-cabin', 'temperature', ''),
('captains-cabin/sensor/humidity', 'captains-cabin', 'humidity', ''),
('captains-cabin/sensor/co2', 'captains-cabin', 'co2', ''),
('crew-sb-aft-cabin/sensor/temperature', 'crew-sb-aft-cabin', 'temperature', ''),
('crew-sb-aft-cabin/sensor/humidity', 'crew-sb-aft-cabin', 'humidity', ''),
('crew-sb-aft-cabin/sensor/co2', 'crew-sb-aft-cabin', 'co2', ''),
('crew-sb-mid-cabin/sensor/temperature', 'crew-sb-mid-cabin', 'temperature', ''),
('crew-sb-mid-cabin/sensor/humidity', 'crew-sb-mid-cabin', 'humidity', ''),
('crew-sb-mid-cabin/sensor/co2', 'crew-sb-mid-cabin', 'co2', ''),
('crew-sb-fwd-cabin/sensor/temperature', 'crew-sb-fwd-cabin', 'temperature', ''),
('crew-sb-fwd-cabin/sensor/humidity', 'crew-sb-fwd-cabin', 'humidity', ''),
('crew-sb-fwd-cabin/sensor/co2', 'crew-sb-fwd-cabin', 'co2', ''),
('crew-ps-mid-cabin/sensor/temperature', 'crew-ps-mid-cabin', 'temperature', ''),
('crew-ps-mid-cabin/sensor/humidity', 'crew-ps-mid-cabin', 'humidity', ''),
('crew-ps-mid-cabin/sensor/co2', 'crew-ps-mid-cabin', 'co2', ''),
('crew-ps-fwd-cabin/sensor/temperature', 'crew-ps-fwd-cabin', 'temperature', ''),
('crew-ps-fwd-cabin/sensor/humidity', 'crew-ps-fwd-cabin', 'humidity', ''),
('crew-ps-fwd-cabin/sensor/co2', 'crew-ps-fwd-cabin', 'co2', ''),
('owners-deckhouse/sensor/temperature', 'owners-deckhouse', 'temperature', ''),
('owners-deckhouse/sensor/humidity', 'owners-deckhouse', 'humidity', ''),
('owners-deckhouse/sensor/co2', 'owners-deckhouse', 'co2', ''),
('main-deckhouse/sensor/temperature', 'main-deckhouse', 'temperature', ''),
('main-deckhouse/sensor/humidity', 'main-deckhouse', 'humidity', ''),
('main-deckhouse/sensor/co2', 'main-deckhouse', 'co2', ''),
('owners-stairway/sensor/temperature', 'owners-stairway', 'temperature', ''),
('owners-stairway/sensor/humidity', 'owners-stairway', 'humidity', ''),
('owners-stairway/sensor/co2', 'owners-stairway', 'co2', ''),
('guest-corridor/sensor/temperature', 'guest-corridor', 'temperature', ''),
('guest-corridor/sensor/humidity', 'guest-corridor', 'humidity', ''),
('guest-corridor/sensor/co2', 'guest-corridor', 'co2', ''),
('polynesian-corridor/sensor/temperature', 'polynesian-corridor', 'temperature', ''),
('polynesian-corridor/sensor/humidity', 'polynesian-corridor', 'humidity', ''),
('polynesian-corridor/sensor/co2', 'polynesian-corridor', 'co2', '');

INSERT INTO amplifiers ("id", "room_id", "name") VALUES
('owners-cabin/amplifier', 'owners-cabin', 'Owners cabin'),
('dutch-cabin/amplifier', 'dutch-cabin', 'Dutch cabin'),
('french-cabin/amplifier', 'french-cabin', 'French cabin'),
('italian-cabin/amplifier', 'italian-cabin', 'Italian cabin'),
('polynesian-cabin/amplifier', 'polynesian-cabin', 'Polynesian cabin'),
('galley/amplifier', 'galley', 'Galley'),
('lounge/amplifier', 'californian-lounge', 'lounge'),
('office/amplifier', 'engineers-office', 'Engineers office'),
('owners-deckhouse/amplifier', 'owners-deckhouse', 'Owners deckhouse'),
('owners-cockpit/amplifier', 'owners-cockpit', 'Owners cockpit'),
('main-deckhouse/amplifier', 'main-deckhouse', 'Main deckhouse'),
('main-cockpit/amplifier', 'main-cockpit', 'Main cockpit');

INSERT INTO blinds ("id", "room_id", "name", "opacity", "group") VALUES
('owners-cabin/main/shear', 'owners-cabin', 'Main', 'shear', 'MAIN'),
('owners-cabin/main/blind', 'owners-cabin', 'Main', 'blind', 'MAIN'),
('owners-cabin/port/shear', 'owners-cabin', 'Port', 'shear', 'PORT'),
('owners-cabin/port/blind', 'owners-cabin', 'Port', 'blind', 'PORT'),
('owners-cabin/starboard/shear', 'owners-cabin', 'Starboard', 'shear', 'STARBOARD'),
('owners-cabin/starboard/blind', 'owners-cabin', 'Starboard', 'blind', 'STARBOARD'),
('owners-cabin/skyline_main/shear', 'owners-cabin', 'Skyline (main)', 'shear', 'SKYLINE_MAIN'),
('owners-cabin/skyline_main/blind', 'owners-cabin', 'Skyline (main)', 'blind', 'SKYLINE_MAIN'),
('owners-cabin/skyline_port/shear', 'owners-cabin', 'Skyline (port)', 'shear', 'SKYLINE_PORT'),
('owners-cabin/skyline_port/blind', 'owners-cabin', 'Skyline (port)', 'blind', 'SKYLINE_PORT'),
('owners-cabin/skyline_starboard/shear', 'owners-cabin', 'Skyline (starboard)', 'shear', 'SKYLINE_STARBOARD'),
('owners-cabin/skyline_starboard/blind', 'owners-cabin', 'Skyline (starboard)', 'blind', 'SKYLINE_STARBOARD'),
('dutch-cabin/blind', 'dutch-cabin', 'Main', 'blind', 'none'),
('french-cabin/blind', 'french-cabin', 'Main', 'blind', 'none'),
('italian-cabin/blind', 'italian-cabin', 'Main', 'blind', 'none'),
('californian-lounge/blind', 'californian-lounge', 'Main', 'blind', 'none'),
('polynesian-cabin/blind', 'polynesian-cabin', 'Main', 'blind', 'none'),
('galley/blind', 'galley', 'Main', 'blind', 'none'),
('crew-mess/blind', 'crew-mess', 'Main', 'blind', 'none'),
('mission-room/blind', 'mission-room', 'Main', 'blind', 'none'),
('laundry/blind', 'laundry', 'Main', 'blind', 'none'),
('engineers-office/blind', 'engineers-office', 'Main', 'blind', 'none'),
('captains-cabin/blind', 'captains-cabin', 'Main', 'blind', 'none'),
('crew-sb-aft-cabin/blind', 'crew-sb-aft-cabin', 'Main', 'blind', 'none'),
('crew-sb-mid-cabin/blind', 'crew-sb-mid-cabin', 'Main', 'blind', 'none'),
('crew-sb-fwd-cabin/blind', 'crew-sb-fwd-cabin', 'Main', 'blind', 'none'),
('crew-ps-mid-cabin/blind', 'crew-ps-mid-cabin', 'Main', 'blind', 'none'),
('crew-ps-fwd-cabin/blind', 'crew-ps-fwd-cabin', 'Main', 'blind', 'none'),
('owners-deckhouse/blind', 'owners-deckhouse', 'Blinds', 'blind', 'none'),
('owners-deckhouse/shear', 'owners-deckhouse', 'Shears', 'shear', 'none'),
('main-deckhouse/blind', 'main-deckhouse', 'Blinds', 'blind', 'none'),
('main-deckhouse/shear', 'main-deckhouse', 'Shears', 'shear', 'none'),
('owners-stairway/blind', 'owners-stairway', 'Main', 'blind', 'none'),
('guest-corridor/blind', 'owners-stairway', 'Main', 'blind', 'none');

INSERT INTO lighting_groups ("id", "room_id", "name") VALUES
('owners-cabin/ambient', 'owners-cabin', 'Ambient'),
('owners-cabin/mood', 'owners-cabin', 'Mood'),
('dutch-cabin/ambient', 'dutch-cabin', 'Ambient'),
('dutch-cabin/mood', 'dutch-cabin', 'Mood'),
('french-cabin/ambient', 'french-cabin', 'Ambient'),
('french-cabin/mood', 'french-cabin', 'Mood'),
('italian-cabin/ambient', 'italian-cabin', 'Ambient'),
('italian-cabin/mood', 'italian-cabin', 'Mood'),
('californian-lounge/ambient', 'californian-lounge', 'Ambient'),
('californian-lounge/mood', 'californian-lounge', 'Mood'),
('polynesian-cabin/ambient', 'polynesian-cabin', 'Ambient'),
('polynesian-cabin/mood', 'polynesian-cabin', 'Mood'),
('galley/ambient', 'galley', 'Ambient'),
('galley/mood', 'galley', 'Mood'),
('crew-mess/ambient', 'crew-mess', 'Ambient'),
('crew-mess/mood', 'crew-mess', 'Mood'),
('mission-room/ambient', 'mission-room', 'Ambient'),
('mission-room/mood', 'mission-room', 'Mood'),
('laundry/ambient', 'laundry', 'Ambient'),
('laundry/mood', 'laundry', 'Mood'),
('engineers-office/ambient', 'engineers-office', 'Ambient'),
('engineers-office/mood', 'engineers-office', 'Mood'),
('captains-cabin/ambient', 'captains-cabin', 'Ambient'),
('captains-cabin/mood', 'captains-cabin', 'Mood'),
('crew-sb-aft-cabin/ambient', 'crew-sb-aft-cabin', 'Ambient'),
('crew-sb-aft-cabin/mood', 'crew-sb-aft-cabin', 'Mood'),
('crew-sb-mid-cabin/ambient', 'crew-sb-mid-cabin', 'Ambient'),
('crew-sb-mid-cabin/mood', 'crew-sb-mid-cabin', 'Mood'),
('crew-sb-fwd-cabin/ambient', 'crew-sb-fwd-cabin', 'Ambient'),
('crew-sb-fwd-cabin/mood', 'crew-sb-fwd-cabin', 'Mood'),
('crew-ps-mid-cabin/ambient', 'crew-ps-mid-cabin', 'Ambient'),
('crew-ps-mid-cabin/mood', 'crew-ps-mid-cabin', 'Mood'),
('crew-ps-fwd-cabin/ambient', 'crew-ps-fwd-cabin', 'Ambient'),
('crew-ps-fwd-cabin/mood', 'crew-ps-fwd-cabin', 'Mood'),
('owners-deckhouse/ambient', 'owners-deckhouse', 'Ambient'),
('owners-deckhouse/mood', 'owners-deckhouse', 'Mood'),
('main-deckhouse/ambient', 'main-deckhouse', 'Ambient'),
('main-deckhouse/mood', 'main-deckhouse', 'Mood'),
('owners-stairway/main', 'owners-stairway', 'Main'),
('guest-corridor/main', 'guest-corridor', 'Main'),
('polynesian-corridor/main', 'polynesian-corridor', 'Main');
