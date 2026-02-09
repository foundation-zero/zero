CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE SCHEMA IF NOT EXISTS loads;

DROP TYPE IF EXISTS unit CASCADE;
CREATE TYPE unit AS ENUM ('tonne', 'ratio', 'bool');


DROP TABLE IF EXISTS loads.sail_positions CASCADE;
CREATE TABLE loads.sail_positions (
    id TEXT PRIMARY KEY
);

DROP TABLE IF EXISTS loads.sails CASCADE;
CREATE TABLE loads.sails (
    id TEXT PRIMARY KEY,
    abbreviation TEXT NOT NULL,
    position_id TEXT NOT NULL REFERENCES loads.sail_positions(id),
    name TEXT NOT NULL,
    variant_name TEXT NOT NULL
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
  id TEXT PRIMARY KEY,
  awa_range numrange NOT NULL CHECK (lower(awa_range) >= 0 AND upper(awa_range) <= 180),
  EXCLUDE USING gist (awa_range WITH &&)
);

DROP TABLE IF EXISTS loads.aws_ranges CASCADE;
CREATE TABLE loads.aws_ranges (
  id SERIAL PRIMARY KEY,
  aws_range numrange NOT NULL CHECK (lower(aws_range) >= 0),
  EXCLUDE USING gist (aws_range WITH &&)
);

DROP TABLE IF EXISTS loads.load_cases CASCADE;
CREATE TABLE loads.load_cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  awa_range_id TEXT NOT NULL REFERENCES loads.awa_ranges(id) ON DELETE RESTRICT,
  aws_range_id INTEGER NOT NULL REFERENCES loads.aws_ranges(id) ON DELETE RESTRICT,
  sail_set_id INTEGER,
  -- Future extensions:
  -- sea_state_id INTEGER REFERENCES loads.sea_states(id),
  -- propulsion_mode_id INTEGER REFERENCES loads.propulsion_modes(id),
  UNIQUE(awa_range_id, aws_range_id, sail_set_id)
);

DROP TABLE IF EXISTS loads.reference_values CASCADE;
CREATE TABLE loads.reference_values (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  load_case_id UUID NOT NULL REFERENCES loads.load_cases(id) ON DELETE RESTRICT,
  variable_id TEXT NOT NULL,
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
INSERT INTO loads.sails (id, abbreviation, position_id, name, variant_name) VALUES
  ('full-main', 'FM', 'main', 'Full Main', 'Full'),
  ('main-reef1', 'M1R', 'main', 'Main 1 Reef', 'Reef 1'),
  ('main-reef2', 'M2R', 'main', 'Main 2 Reef', 'Reef 2'),
  ('main-reef3', 'M3R', 'main', 'Main 3 Reef', 'Reef 3'),
  ('trisail', 'TS', 'main', 'Trisail', 'Trisail'),
  ('full-mizzen', 'FMZ', 'mizzen', 'Full Mizzen', 'Full'),
  ('mizzen-reef1', 'MZ1R', 'mizzen', 'Mizzen 1 Reef', 'Reef 1'),
  ('mizzen-reef2', 'MZ2R', 'mizzen', 'Mizzen 2 Reef', 'Reef 2'),
  ('utility-main', 'UM', 'main', 'Utility Main', 'Utility'),
  ('blade', 'B', 'fore-outer', 'Blade', 'Blade'),
  ('code-zero', 'C0', 'fore-outer', 'Code Zero', 'Code Zero'),
  ('A3', 'A3', 'fore-outer', 'A3', 'A3'),
  ('A2', 'A2', 'fore-outer', 'A2', 'A2'),
  ('storm-jib', 'SJ', 'fore-inner', 'Storm Jib', 'Storm Jib'),
  ('staysail', 'SS', 'fore-inner', 'Staysail', 'Staysail'),
  ('mizzen-jib', 'MZJ', 'mizzen-fore', 'Mizzen Jib', 'Jib'),
  ('mizzen-staysail', 'MZSS', 'mizzen-fore', 'Staysail', 'Staysail');

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
INSERT INTO loads.awa_ranges (id, awa_range) VALUES
    ('upwind', '[0,60)'),
    ('reaching', '[60,120)'),
    ('downwind', '[120,180)');

-- Define AWS ranges
INSERT INTO loads.aws_ranges (aws_range) VALUES
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

-- Example reference value for a specific load case
INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    'main-sheet-load',
    load_cases.id,
    0.0,
    3.0,
    6.0,
    8.0,
    10.0
FROM loads.load_cases
JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
WHERE awa_range.id = 'upwind';

INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    'main-sheet-load',
    load_cases.id,
    0.0,
    1.0,
    5.0,
    6.0,
    8.0
FROM loads.load_cases
JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
WHERE awa_range.id = 'reaching';

INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    'main-sheet-load',
    load_cases.id,
    0.0,
    1.0,
    2.0,
    3.0,
    4.0
FROM loads.load_cases
JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
WHERE awa_range.id = 'downwind';

INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    'main-vang-load',
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
WHERE awa_range.id = 'downwind' AND aws_range.aws_range = '[15,20)'::numrange
AND sail_set.sails = ARRAY['blade', 'full-main', 'full-mizzen'];

INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    'main-traveler-relative-position',
    load_cases.id,
    NULL,
    NULL,
    .5,
    NULL,
    .8
FROM loads.load_cases
JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
WHERE awa_range.id = 'upwind'
