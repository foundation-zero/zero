CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE SCHEMA IF NOT EXISTS loads;

DROP TYPE IF EXISTS unit CASCADE;
CREATE TYPE unit AS ENUM ('tonne', 'percent', 'on-off');


DROP TABLE IF EXISTS loads.sail_positions CASCADE;
CREATE TABLE loads.sail_positions (
    id TEXT PRIMARY KEY
);

DROP TABLE IF EXISTS loads.sails CASCADE;
CREATE TABLE loads.sails (
    id TEXT PRIMARY KEY,              
    abbreviation TEXT NOT NULL,               
    position_id TEXT NOT NULL REFERENCES loads.sail_positions(id),       
    name TEXT NOT NULL              
);

DROP TABLE IF EXISTS loads.sail_sets CASCADE;
CREATE TABLE loads.sail_sets (
    sail_set_id INTEGER NOT NULL,
    position_id TEXT NOT NULL REFERENCES loads.sail_positions(id),
    sail_id TEXT REFERENCES loads.sails(id)
);

DROP VIEW IF EXISTS loads.sail_sets_combined CASCADE;
CREATE VIEW loads.sail_sets_combined AS
-- This view makes looking up the sail case easier by aggregating the sails into an array
-- Lookup can be done by matching the (ordered) array of sails
SELECT
    sail_set_id as id,
    ARRAY_AGG(sail_id ORDER BY sail_id) FILTER (WHERE sail_id IS NOT NULL) AS sails
FROM loads.sail_sets
GROUP BY sail_set_id;

DROP TABLE IF EXISTS loads.awa_ranges CASCADE;
CREATE TABLE loads.awa_ranges (
  id SERIAL PRIMARY KEY,
  awa numrange NOT NULL CHECK (lower(awa) >= 0 AND upper(awa) <= 180),
  EXCLUDE USING gist (awa WITH &&)
);

DROP TABLE IF EXISTS loads.aws_ranges CASCADE;
CREATE TABLE loads.aws_ranges (
  id SERIAL PRIMARY KEY,
  aws numrange NOT NULL CHECK (lower(aws) >= 0),
  EXCLUDE USING gist (aws WITH &&)
);

DROP TABLE IF EXISTS loads.load_cases CASCADE;
CREATE TABLE loads.load_cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  awa_range_id INTEGER NOT NULL REFERENCES loads.awa_ranges(id) ON DELETE RESTRICT,
  aws_range_id INTEGER NOT NULL REFERENCES loads.aws_ranges(id) ON DELETE RESTRICT,
  sail_set_id INTEGER,
  -- Future extensions:
  -- sea_state_id INTEGER REFERENCES loads.sea_states(id),
  -- propulsion_mode_id INTEGER REFERENCES loads.propulsion_modes(id),
  UNIQUE(awa_range_id, aws_range_id, sail_set_id)
);

DROP TABLE IF EXISTS loads.variables CASCADE;
CREATE TABLE loads.variables (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  unit unit NOT NULL,
  tag TEXT,
  minimum_value NUMERIC,
  maximum_value NUMERIC
);

DROP TABLE IF EXISTS loads.reference_values CASCADE;
CREATE TABLE loads.reference_values (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  load_case_id UUID NOT NULL REFERENCES loads.load_cases(id) ON DELETE RESTRICT,
  variable_id TEXT NOT NULL REFERENCES loads.variables(id) ON DELETE RESTRICT,
  alarm_low NUMERIC,
  warning_low NUMERIC,
  target NUMERIC,
  warning_high NUMERIC,
  alarm_high NUMERIC,
  UNIQUE(load_case_id, variable_id),
  CHECK (
    (alarm_low IS NULL OR warning_low IS NULL OR alarm_low <= warning_low) AND
    (warning_low IS NULL OR target IS NULL OR warning_low <= target) AND
    (warning_high IS NULL OR target IS NULL OR target <= warning_high) AND
    (warning_high IS NULL OR alarm_high IS NULL OR warning_high <= alarm_high)
  )
);

-- Define sail positions
INSERT INTO loads.sail_positions (id) VALUES
  ('main'),
  ('mizzen'),
  ('fore-inner'),
  ('fore-outer'),
  ('mizzen-fore');

-- Define sails
INSERT INTO loads.sails (id, abbreviation, position_id, name) VALUES
  ('full-main', 'FM', 'main', 'Full Main'),
  ('main-reef1', 'M1R', 'main', 'Main 1 Reef'),
  ('main-reef2', 'M2R', 'main', 'Main 2 Reef'),
  ('main-reef3', 'M3R', 'main', 'Main 3 Reef'),
  ('trisail', 'TS', 'main', 'Trisail'),
  ('full-mizzen', 'FMZ', 'mizzen', 'Full Mizzen'),
  ('mizzen-reef1', 'MZ1R', 'mizzen', 'Mizzen 1 Reef'),
  ('mizzen-reef2', 'MZ2R', 'mizzen', 'Mizzen 2 Reef'),
  ('blade', 'J3', 'fore-outer', 'Blade'),
  ('code-zero', 'C0', 'fore-outer', 'Code Zero'),
  ('genoa', 'A3', 'fore-outer', 'Furling Genoa'),
  ('gennaker', 'A2', 'fore-outer', 'Gennaker'),
  ('storm-jib', 'J5', 'fore-inner', 'Storm Jib'),
  ('staysail', 'J4', 'fore-inner', 'Staysail'),
  ('mizzen-jib', 'MZJ', 'mizzen-fore', 'Mizzen Jib'),
  ('mizzen-genoa', 'MZG', 'mizzen-fore', 'Mizzen Genoa');

-- Generate all possible sail sets based on position (including those with NULLs for missing sails)
WITH RECURSIVE indexed_positions AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY id) AS position_index,
        id as position
    FROM loads.sail_positions
),
options AS (
    SELECT
        position,
        id as sail
    FROM loads.sails
    JOIN indexed_positions
        ON loads.sails.position_id = indexed_positions.position

    UNION ALL

    SELECT
        id as position,
        NULL::TEXT as sail
    FROM loads.sail_positions
),
combinations AS (
    SELECT
        indexed_positions.position_index,
        ARRAY[options.sail]::TEXT[] AS sail_set
    FROM indexed_positions
    JOIN options
        ON options.position = indexed_positions.position
    WHERE indexed_positions.position_index = 1
  
    UNION ALL

    SELECT
        next_position.position_index,
        combinations.sail_set || options.sail
    FROM combinations
    JOIN indexed_positions AS next_position
        ON next_position.position_index = combinations.position_index + 1
    JOIN options
        ON options.position = next_position.position
),
complete_combinations AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY sail_set) - 1 id,
        sail_set
    FROM combinations
    WHERE position_index = (SELECT MAX(position_index) FROM indexed_positions)
),
flat_sail_sets AS (
    SELECT
        complete_combinations.id,
        indexed_positions.position,
        complete_combinations.sail_set[indexed_positions.position_index] AS sail
    FROM complete_combinations
    CROSS JOIN indexed_positions
)
INSERT INTO loads.sail_sets (sail_set_id, position_id, sail_id)
SELECT
    id,
    position,
    sail
FROM flat_sail_sets
ORDER BY id, position;

-- Define AWA ranges
INSERT INTO loads.awa_ranges (awa) VALUES
  ('[0,20)'),
  ('[20,25)'),
  ('[25,30)'),
  ('[30,40)'),
  ('[40,60)'),
  ('[60,80)'),
  ('[80,120)'),
  ('[120,180)');

-- Define AWS ranges
INSERT INTO loads.aws_ranges (aws) VALUES
  ('[0,10)'),
  ('[10,15)'),
  ('[15,20)'),
  ('[20,25)'),
  ('[25,30)'),
  ('[30,40)'),
  ('[40,)');

-- Define load cases
INSERT INTO loads.load_cases (awa_range_id, aws_range_id, sail_set_id)
SELECT 
    awa_range.id AS awa_range_id,
    aws_range.id AS aws_range_id,
    sail_set_ids.sail_set_id AS sail_set_id
FROM (SELECT DISTINCT sail_set_id from loads.sail_sets) as sail_set_ids
CROSS JOIN loads.awa_ranges AS awa_range
CROSS JOIN loads.aws_ranges AS aws_range;

-- Define variables
INSERT INTO loads.variables (id, name, unit) VALUES
  ('main-sheet-load', 'Main Sheet Load', 'tonne'),
  ('main-sheet-position', 'Main Sheet Position', 'percent'),
  ('main-traveler-position', 'Main Traveler Position', 'percent'),
  ('main-preventer-load', 'Main Preventer Load', 'tonne'),
  ('main-preventer-position', 'Main Preventer Position', 'percent'),
  ('main-vang-load', 'Main Vang Load', 'tonne'),
  ('main-vang-position', 'Main Vang Position', 'percent'),
  ('main-outhaul-load', 'Main Outhaul Load', 'tonne'),
  ('main-outhaul-position', 'Main Outhaul Position', 'percent'),
  ('main-halyard-load', 'Main Halyard Load', 'tonne'),
  ('main-halyard-position', 'Main Halyard Position', 'percent'),
  ('main-cunningham-load', 'Main Cunningham Load', 'tonne'),
  ('main-cunningham-position', 'Main Cunningham Position', 'percent'),
  ('main-runner-load-ps', 'Main Runner Load Port Side', 'tonne'),
  ('main-runner-position-ps', 'Main Runner Position Port Side', 'percent'),
  ('main-runner-load-sb', 'Main Runner Load Starboard Side', 'tonne'),
  ('main-runner-position-sb', 'Main Runner Position Starboard Side', 'percent'),
  ('main-checkstay-load-ps', 'Main Checkstay Load Port Side', 'tonne'),
  ('main-checkstay-load-sb', 'Main Checkstay Load Starboard Side', 'tonne'),
  ('main-checkstay-position-sb', 'Main Checkstay Position Starboard Side', 'percent'),
  ('main-checkstay-deflector-load-ps', 'Main Checkstay Deflector Load Port Side', 'tonne'),
  ('main-checkstay-deflector-position-ps', 'Main Checkstay Deflector Position Port Side', 'percent'),
  ('main-checkstay-deflector-load-sb', 'Main Checkstay Deflector Load Starboard Side', 'tonne'),
  ('main-checkstay-deflector-position-sb', 'Main Checkstay Deflector Position Starboard Side', 'percent'),
  ('main-headboard-lock', 'Main Headboard Lock', 'on-off'),
  ('main-headboard-overhoist', 'Main Headboard Overhoist', 'on-off'),
  ('main-reef-1-lock', 'Main Reef 1 Lock', 'on-off'),
  ('main-reef-1-overhoist', 'Main Reef 1 Overhoist', 'on-off'),
  ('main-reef-2-lock', 'Main Reef 2 Lock', 'on-off'),
  ('main-reef-2-overhoist', 'Main Reef 2 Overhoist', 'on-off'),
  ('main-reef-3-lock', 'Main Reef 3 Lock', 'on-off'),
  ('main-reef-3-overhoist', 'Main Reef 3 Overhoist', 'on-off'),
  ('main-boom-reef-1-lock', 'Main Boom Reef 1 Lock', 'on-off'),
  ('main-boom-reef-1-overhoist', 'Main Boom Reef 1 Overhoist', 'on-off'),
  ('main-boom-reef-2-lock', 'Main Boom Reef 2 Lock', 'on-off'),
  ('main-boom-reef-2-overhoist', 'Main Boom Reef 2 Overhoist', 'on-off'),
  ('main-boom-reef-3-lock', 'Main Boom Reef 3 Lock', 'on-off'),
  ('main-boom-reef-3-overhoist', 'Main Boom Reef 3 Overhoist', 'on-off'),
  ('mizzen-sheet-load', 'Mizzen Sheet Load', 'tonne'),
  ('mizzen-sheet-position', 'Mizzen Sheet Position', 'percent'),
  ('mizzen-preventer-load', 'Mizzen Preventer Load', 'tonne'),
  ('mizzen-vang-load', 'Mizzen Vang Load', 'tonne'),
  ('mizzen-vang-position', 'Mizzen Vang Position', 'percent'),
  ('mizzen-outhaul-load', 'Mizzen Outhaul Load', 'tonne'),
  ('mizzen-outhaul-position', 'Mizzen Outhaul Position', 'percent'),
  ('mizzen-halyard-load', 'Mizzen Halyard Load', 'tonne'),
  ('mizzen-halyard-position', 'Mizzen Halyard Position', 'percent'),
  ('mizzen-cunningham-load', 'Mizzen Cunningham Load', 'tonne'),
  ('mizzen-cunningham-position', 'Mizzen Cunningham Position', 'percent'),
  ('mizzen-runner-load-ps', 'Mizzen Runner Load Port Side', 'tonne'),
  ('mizzen-runner-position-ps', 'Mizzen Runner Position Port Side', 'percent'),
  ('mizzen-runner-load-sb', 'Mizzen Runner Load Starboard Side', 'tonne'),
  ('mizzen-runner-position-sb', 'Mizzen Runner Position Starboard Side', 'percent'),
  ('mizzen-checkstay-load-ps', 'Mizzen Checkstay Load Port Side', 'tonne'),
  ('mizzen-checkstay-position-ps', 'Mizzen Checkstay Position Port Side', 'percent'),
  ('mizzen-checkstay-load-sb', 'Mizzen Checkstay Load Starboard Side', 'tonne'),
  ('mizzen-checkstay-position-sb', 'Mizzen Checkstay Position Starboard Side', 'percent'),
  ('mizzen-checkstay-deflector-load-ps', 'Mizzen Checkstay Deflector Load Port Side', 'tonne'),
  ('mizzen-checkstay-deflector-position-ps', 'Mizzen Checkstay Deflector Position Port Side', 'percent'),
  ('mizzen-checkstay-deflector-load-sb', 'Mizzen Checkstay Deflector Load Starboard Side', 'tonne'),
  ('mizzen-checkstay-deflector-position-sb', 'Mizzen Checkstay Deflector Position Starboard Side', 'percent'),
  ('mizzen-headboard-lock', 'Mizzen Headboard Lock', 'on-off'),
  ('mizzen-headboard-overhoist', 'Mizzen Headboard Overhoist', 'on-off'),
  ('mizzen-reef-1-lock', 'Mizzen Reef 1 Lock', 'on-off'),
  ('mizzen-reef-1-overhoist', 'Mizzen Reef 1 Overhoist', 'on-off'),
  ('mizzen-reef-2-lock', 'Mizzen Reef 2 Lock', 'on-off'),
  ('mizzen-reef-2-overhoist', 'Mizzen Reef 2 Overhoist', 'on-off'),
  ('mizzen-boom-reef-1-lock', 'Mizzen Boom Reef 1 Lock', 'on-off'),
  ('mizzen-boom-reef-1-overhoist', 'Mizzen Boom Reef 1 Overhoist', 'on-off'),
  ('mizzen-boom-reef-2-lock', 'Mizzen Boom Reef 2 Lock', 'on-off'),
  ('mizzen-boom-reef-2-overhoist', 'Mizzen Boom Reef 2 Overhoist', 'on-off');

-- Example reference value for a specific load case
INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT 
    'main-sheet-load',
    load_cases.id,
    NULL,
    NULL,
    NULL,
    NULL,
    15.0
FROM loads.load_cases
JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
JOIN loads.aws_ranges AS aws_range ON load_cases.aws_range_id = aws_range.id
JOIN loads.sail_sets_combined AS sail_set ON load_cases.sail_set_id = sail_set.id
WHERE awa_range.awa = '[25,30)'::numrange AND aws_range.aws = '[15,20)'::numrange
AND sail_set.sails = ARRAY['blade', 'full-main', 'full-mizzen'];