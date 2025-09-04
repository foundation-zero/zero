-- The various sea states (to be expanded)
DROP TYPE IF EXISTS sea_state CASCADE;
CREATE TYPE sea_state AS ENUM ('wet');

DROP TYPE IF EXISTS unit CASCADE;
CREATE TYPE unit AS ENUM ('tonne', 'meter', 'knot', 'percentage');

DROP TYPE IF EXISTS pcs_mode CASCADE;
CREATE TYPE pcs_mode AS ENUM ('idle', 'regeneration', 'propulsion');

DROP TABLE IF EXISTS masts CASCADE;
CREATE TABLE masts (
  id TEXT PRIMARY KEY,
  name TEXT
);

-- sails also includes different reefs of the main and mizzen sails. i.e. full-main-sail, main-sail-reef1, main-sail-reef2 are all rows in this table
DROP TABLE IF EXISTS sails CASCADE;
CREATE TABLE sails (
  id TEXT PRIMARY KEY,
  mast_id TEXT NOT NULL REFERENCES masts(id) ON DELETE RESTRICT,
  name TEXT
);

DROP TABLE IF EXISTS sail_sets CASCADE;
CREATE TABLE sail_sets (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

DROP TABLE IF EXISTS sail_sets_sails CASCADE;
CREATE TABLE sail_sets_sails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sail_id TEXT NOT NULL REFERENCES sails(id) ON DELETE RESTRICT,
  sail_set_id TEXT NOT NULL REFERENCES sail_sets(id) ON DELETE RESTRICT
);

DROP VIEW IF EXISTS sail_sets_combined CASCADE;
-- This view makes looking up the sail case easier by aggregating the sails into an array
-- Lookup can be done by matching the (ordered) array of sails
CREATE VIEW sail_sets_combined AS
SELECT sail_sets.*, ARRAY_AGG(sail_sets_sails.sail_id ORDER BY sail_sets_sails.sail_id) AS sails
FROM sail_sets
JOIN sail_sets_sails ON sail_sets_sails.sail_set_id = sail_sets.id
GROUP BY sail_sets.id;

DROP TYPE IF EXISTS value_definition_scope CASCADE;
CREATE TYPE value_definition_scope AS ENUM ('mast_specific', 'general');

DROP TABLE IF EXISTS value_definitions CASCADE;
CREATE TABLE value_definitions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  unit unit NOT NULL,
  scope value_definition_scope NOT NULL
);

DROP TABLE IF EXISTS conditions CASCADE;
CREATE TABLE conditions (
  id TEXT PRIMARY KEY,
  sail_set_id TEXT REFERENCES sail_sets(id) ON DELETE RESTRICT,
  name TEXT NOT NULL,
  sea_state sea_state NOT NULL,
  awa numrange NOT NULL CHECK (lower(awa) >= 0 AND upper(awa) <= 180), -- sailing is symmetrical, so only 0-180 degrees needed, in fact a range might actually be -90..-45 & 45..90
  aws numrange NOT NULL CHECK (lower(aws) >= 0),
  pcs_mode_aft pcs_mode[] NOT NULL, -- the set of pcs modes in this sail case
  pcs_mode_fwd pcs_mode[] NOT NULL
);

DROP TABLE IF EXISTS reference_values;
CREATE TABLE reference_values (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sail_case_id TEXT NOT NULL REFERENCES conditions(id) ON DELETE RESTRICT,
  mast_id TEXT REFERENCES masts(id) ON DELETE RESTRICT,
  value_definition_id TEXT NOT NULL REFERENCES value_definitions(id) ON DELETE RESTRICT,
  value NUMERIC NOT NULL,
  error_too_low NUMERIC,
  warning_too_low NUMERIC,
  warning_too_high NUMERIC,
  error_too_high NUMERIC
);

-- Seed
-- Incomplete for now, just to get started
INSERT INTO masts (id, name) VALUES
  ('main', 'Main mast'),
  ('mizzen', 'Mizzen mast');

INSERT INTO sails (id, mast_id, name) VALUES
  ('full-main-sail', 'main', 'Full Main Sail'),
  ('main-sail-reef1', 'main', 'Main Sail Reef 1'),
  ('main-sail-reef2', 'main', 'Main Sail Reef 2'),
  ('blade', 'main', 'Main Blade'),
  ('main-staysail', 'main', 'Main Staysail'),
  ('full-mizzen-sail', 'mizzen', 'Full Mizzen Sail'),
  ('mizzen-sail-reef1', 'mizzen', 'Mizzen Sail Reef 1'),
  ('mizzen-sail-reef2', 'mizzen', 'Mizzen Sail Reef 2'),
  ('mizzen-jib', 'mizzen', 'Mizzen Jib'),
  ('mizzen-staysail', 'mizzen', 'Mizzen Staysail');

INSERT INTO sail_sets (id, name) VALUES
  ('upwind-blade', 'Upwind Blade'),
  ('reach-blade-mzj', 'Reach Blade with Mizzen Jib');

INSERT INTO sail_sets_sails (sail_set_id, sail_id) VALUES
  ('upwind-blade', 'full-main-sail'),
  ('upwind-blade', 'blade'),
  ('upwind-blade', 'full-mizzen-sail'),

  ('reach-blade-mzj', 'full-main-sail'),
  ('reach-blade-mzj', 'blade'),
  ('reach-blade-mzj', 'mizzen-jib'),
  ('reach-blade-mzj', 'full-mizzen-sail');

INSERT INTO value_definitions (id, name, unit, scope) VALUES
  ('headstay-load', 'Headstay load', 'tonne', 'mast_specific'),
  ('boatspeed', 'Boat Speed', 'knot', 'general');

INSERT INTO conditions (id, sail_set_id, name, sea_state, awa, aws, pcs_mode_aft, pcs_mode_fwd) VALUES
  ('light-wind-close-hauled', 'reach-blade-mzj', 'Light wind close-hauled', 'wet', '[0,45)', '[0,10)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]),
  ('light-wind-beam-reach', 'upwind-blade', 'Light wind beam reach', 'wet', '[45,135)', '[0,10)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]),
  ('light-wind-broad-reach', 'upwind-blade', 'Light wind broad reach', 'wet', '[135,180]', '[0,10)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]),
  ('moderate-wind-close-hauled', 'upwind-blade', 'Moderate wind close-hauled', 'wet', '[0,45)', '[10,20)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]),
  ('moderate-wind-beam-reach', 'upwind-blade', 'Moderate wind beam reach', 'wet', '[45,135)', '[10,20)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]),
  ('moderate-wind-broad-reach', 'upwind-blade', 'Moderate wind broad reach', 'wet', '[135,180]', '[10,20)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]),
  ('strong-wind-close-hauled', 'reach-blade-mzj', 'Strong wind close-hauled', 'wet', '[0,45)', '[20,30)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]),
  ('strong-wind-beam-reach', 'upwind-blade', 'Strong wind beam reach', 'wet', '[45,135)', '[20,30)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]),
  ('strong-wind-broad-reach', 'upwind-blade', 'Strong wind broad reach', 'wet', '[135,180]', '[20,30)', ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[], ARRAY['propulsion', 'regeneration', 'idle']::pcs_mode[]);

INSERT INTO reference_values (sail_case_id, mast_id, value_definition_id, value) VALUES
  ('light-wind-close-hauled', 'main', 'headstay-load', 2.0),
  ('light-wind-close-hauled', 'mizzen', 'headstay-load', 1.0),
  ('light-wind-close-hauled', NULL, 'boatspeed', 5.0),

  ('light-wind-beam-reach', 'main', 'headstay-load', 2.5),
  ('light-wind-beam-reach', 'mizzen', 'headstay-load', 1.2),
  ('light-wind-beam-reach', NULL, 'boatspeed', 6.0),

  ('light-wind-broad-reach', 'main', 'headstay-load', 2.0),
  ('light-wind-broad-reach', 'mizzen', 'headstay-load', 1.0),
  ('light-wind-broad-reach', NULL, 'boatspeed', 5.5),

  ('moderate-wind-close-hauled', 'main', 'headstay-load', 3.5),
  ('moderate-wind-close-hauled', 'mizzen', 'headstay-load', 1.8),
  ('moderate-wind-close-hauled', NULL, 'boatspeed', 7.0),

  ('moderate-wind-beam-reach', 'main', 'headstay-load', 4.0),
  ('moderate-wind-beam-reach', 'mizzen', 'headstay-load', 2.0),
  ('moderate-wind-beam-reach', NULL, 'boatspeed', 8.0),

  ('moderate-wind-broad-reach', 'main', 'headstay-load', 3.5),
  ('moderate-wind-broad-reach', 'mizzen', 'headstay-load', 1.8),
  ('moderate-wind-broad-reach', NULL, 'boatspeed', 7.5),

  ('strong-wind-close-hauled', 'main', 'headstay-load', 5.0),
  ('strong-wind-close-hauled', 'mizzen', 'headstay-load', 2.5),
  ('strong-wind-close-hauled', NULL, 'boatspeed', 9.0),

  ('strong-wind-beam-reach', 'main', 'headstay-load', 6.0),
  ('strong-wind-beam-reach', 'mizzen', 'headstay-load', 3.0),
  ('strong-wind-beam-reach', NULL, 'boatspeed', 10.0),

  ('strong-wind-broad-reach', 'main', 'headstay-load', 5.5),
  ('strong-wind-broad-reach', 'mizzen', 'headstay-load', 2.5),
  ('strong-wind-broad-reach', NULL, 'boatspeed', 9.5);
