CREATE SCHEMA IF NOT EXISTS domestic;

-- Master table for rooms
CREATE TABLE domestic.rooms (
  "id" TEXT PRIMARY KEY,
  "name" TEXT,
  "group" TEXT
);

-- Master table for blinds per room
CREATE TABLE domestic.blinds (
  "id" TEXT PRIMARY KEY,
  "room_id" VARCHAR REFERENCES domestic.rooms("id"),
  "name" TEXT,
  "opacity" TEXT,
  "group" TEXT,
  "level" REAL
);

CREATE TABLE domestic.air_conditioning (
  "id" TEXT PRIMARY KEY REFERENCES domestic.rooms("id"),
  "temperature_setpoint" REAL,
  "humidity_setpoint" REAL,
  "actual_temperature" REAL,
  "actual_humidity" REAL
);

CREATE TABLE domestic.ventilation (
  "id" TEXT PRIMARY KEY REFERENCES domestic.rooms("id"),
  "co2_setpoint" REAL,
  "actual_co2" REAL
);

-- Master table for lighting groups per room
CREATE TABLE domestic.lighting_groups (
  "id" VARCHAR PRIMARY KEY,
  "room_id" VARCHAR REFERENCES domestic.rooms("id"),
  "name" TEXT,
  "level" REAL
);

-- Master table for amplifiers per room
CREATE TABLE domestic.amplifiers (
  "id" VARCHAR PRIMARY KEY REFERENCES domestic.rooms("id"),
  "name" TEXT,
  "on" BOOLEAN
);

-- Legacy room_sensors tables removed in favor of room_state + dedicated logs above.

INSERT INTO domestic.rooms ("id", "name", "group") VALUES
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
('office', 'Office', 'FORE'),
('lounge', 'Lounge', 'FORE'),
('owners-deckhouse', 'Owners deckhouse', 'UPPERDECK'),
('owners-cockpit', 'Owners cockpit', 'AFT'),
('main-deckhouse', 'Main deckhouse', 'UPPERDECK'),
('main-cockpit', 'Main cockpit', 'UPPERDECK'),
('owners-stairway', 'Owners stairway', 'HALLWAYS'),
('guest-corridor', 'Guest corridor', 'HALLWAYS'),
('polynesian-corridor', 'Polynesian corridor', 'HALLWAYS');


INSERT INTO domestic.amplifiers ("id", "name") VALUES
('owners-cockpit', 'Owners cockpit'),
('owners-deckhouse', 'Owners deckhouse'),
('owners-cabin', 'Owners cabin'),
('main-cockpit', 'Main cockpit'),
('italian-cabin', 'Italian cabin'),
('galley', 'Galley'),
('french-cabin', 'French cabin'),
('dutch-cabin', 'Dutch cabin'),
('polynesian-cabin', 'Polynesian cabin'),
('main-deckhouse', 'Main deckhouse'),
('office', 'Office'),
('lounge', 'lounge');

INSERT INTO domestic.blinds ("id", "room_id", "name", "opacity", "group") VALUES
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

INSERT INTO domestic.lighting_groups ("id", "room_id", "name") VALUES
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
