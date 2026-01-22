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
  ('utility-main', 'UM', 'main', 'Utility Main'),
  ('blade', 'B', 'fore-outer', 'Blade'),
  ('code-zero', 'C0', 'fore-outer', 'Code Zero'),
  ('A3', 'A3', 'fore-outer', 'A3'),
  ('A2', 'A2', 'fore-outer', 'A2'),
  ('storm-jib', 'SJ', 'fore-inner', 'Storm Jib'),
  ('staysail', 'SS', 'fore-inner', 'Staysail'),
  ('mizzen-jib', 'MZJ', 'mizzen-fore', 'Mizzen Jib'),
  ('mizzen-staysail', 'MZSS', 'mizzen-fore', 'Mizzen Staysail');

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

-- Define variables
INSERT INTO loads.variables (id, name, unit, minimum_value, maximum_value) VALUES
    ('blade-adjuster-load', 'Blade Adjuster Load', 'tonne', 0, NULL),
    ('blade-adjuster-position', 'Blade Adjuster Position', 'ratio', 0, 1),
    ('blade-adjuster-relative-position', 'Blade Adjuster Relative Position', 'ratio', 0, 1),
    ('blade-cunningham-load', 'Blade Cunningham Load', 'tonne', 0, NULL),
    ('blade-cunningham-position', 'Blade Cunningham Position', 'ratio', 0, 1),
    ('blade-cunningham-relative-position', 'Blade Cunningham Relative Position', 'ratio', 0, 1),
    ('blade-sheet-feeder-ps-load', 'Blade Sheet Feeder Ps Load', 'tonne', 0, NULL),
    ('blade-sheet-feeder-sb-load', 'Blade Sheet Feeder Sb Load', 'tonne', 0, NULL),
    ('blade-tweaker-ps-load', 'Blade Tweaker Ps Load', 'tonne', 0, NULL),
    ('blade-tweaker-ps-position', 'Blade Tweaker Ps Position', 'ratio', 0, 1),
    ('blade-tweaker-ps-relative-position', 'Blade Tweaker Ps Relative Position', 'ratio', 0, 1),
    ('blade-tweaker-sb-load', 'Blade Tweaker Sb Load', 'tonne', 0, NULL),
    ('blade-tweaker-sb-position', 'Blade Tweaker Sb Position', 'ratio', 0, 1),
    ('blade-tweaker-sb-relative-position', 'Blade Tweaker Sb Relative Position', 'ratio', 0, 1),
    ('code-zero-lock', 'Code Zero Lock', 'bool', 0, 1),
    ('code-zero-overhoist', 'Code Zero Overhoist', 'bool', 0, 1),
    ('code-zero-tack-load', 'Code Zero Tack Load', 'tonne', 0, NULL),
    ('code-zero-tack-position', 'Code Zero Tack Position', 'ratio', 0, 1),
    ('code-zero-tack-relative-position', 'Code Zero Tack Relative Position', 'ratio', 0, 1),
    ('main-boom-reef-1-lock', 'Main Boom Reef 1 Lock', 'bool', 0, 1),
    ('main-boom-reef-2-lock', 'Main Boom Reef 2 Lock', 'bool', 0, 1),
    ('main-boom-reef-3-lock', 'Main Boom Reef 3 Lock', 'bool', 0, 1),
    ('main-checkstay-deflector-load', 'Main Checkstay Deflector Load', 'tonne', 0, NULL),
    ('main-checkstay-deflector-relative-position', 'Main Checkstay Deflector Relative Position', 'ratio', 0, 1),
    ('main-checkstay-ps-load', 'Main Checkstay Ps Load', 'tonne', 0, NULL),
    ('main-checkstay-sb-load', 'Main Checkstay Sb Load', 'tonne', 0, NULL),
    ('main-cunningham-load', 'Main Cunningham Load', 'tonne', 0, NULL),
    ('main-cunningham-position', 'Main Cunningham Position', 'ratio', 0, 1),
    ('main-cunningham-relative-position', 'Main Cunningham Relative Position', 'ratio', 0, 1),
    ('main-halyard-load', 'Main Halyard Load', 'tonne', 0, NULL),
    ('main-halyard-lock-full', 'Main Halyard Lock Full', 'bool', 0, 1),
    ('main-halyard-overhoist-full', 'Main Halyard Overhoist Full', 'bool', 0, 1),
    ('main-halyard-reef-1-lock', 'Main Halyard Reef 1 Lock', 'bool', 0, 1),
    ('main-halyard-reef-1-overhoist', 'Main Halyard Reef 1 Overhoist', 'bool', 0, 1),
    ('main-halyard-reef-2-lock', 'Main Halyard Reef 2 Lock', 'bool', 0, 1),
    ('main-halyard-reef-2-overhoist', 'Main Halyard Reef 2 Overhoist', 'bool', 0, 1),
    ('main-halyard-reef-3-lock', 'Main Halyard Reef 3 Lock', 'bool', 0, 1),
    ('main-halyard-reef-3-overhoist', 'Main Halyard Reef 3 Overhoist', 'bool', 0, 1),
    ('main-halyard-relative-position', 'Main Halyard Relative Position', 'ratio', 0, 1),
    ('main-outhaul-load', 'Main Outhaul Load', 'tonne', 0, NULL),
    ('main-outhaul-position', 'Main Outhaul Position', 'ratio', 0, 1),
    ('main-outhaul-relative-position', 'Main Outhaul Relative Position', 'ratio', 0, 1),
    ('main-preventer-load', 'Main Preventer Load', 'tonne', 0, NULL),
    ('main-preventer-position', 'Main Preventer Position', 'ratio', 0, 1),
    ('main-preventer-relative-position', 'Main Preventer Relative Position', 'ratio', 0, 1),
    ('main-runner-ps-relative-position', 'Main Runner Ps Relative Position', 'ratio', 0, 1),
    ('main-runner-sb-relative-position', 'Main Runner Sb Relative Position', 'ratio', 0, 1),
    ('main-runner-ps-load', 'Main Runner Ps Load', 'tonne', 0, NULL),
    ('main-runner-sb-load', 'Main Runner Sb Load', 'tonne', 0, NULL),
    ('main-sheet-load', 'Main Sheet Load', 'tonne', 0, NULL),
    ('main-sheet-position', 'Main Sheet Position', 'ratio', 0, 1),
    ('main-sheet-relative-position', 'Main Sheet Relative Position', 'ratio', 0, 1),
    ('main-traveler-relative-position', 'Main Traveler Relative Position', 'ratio', 0, 1),
    ('main-vang-load', 'Main Vang Load', 'tonne', 0, NULL),
    ('main-vang-position', 'Main Vang Position', 'ratio', 0, 1),
    ('main-vang-relative-position', 'Main Vang Relative Position', 'ratio', 0, 1),
    ('mizzen-boom-reef-1-lock', 'Mizzen Boom Reef 1 Lock', 'bool', 0, 1),
    ('mizzen-boom-reef-2-lock', 'Mizzen Boom Reef 2 Lock', 'bool', 0, 1),
    ('mizzen-checkstay-deflector-load', 'Mizzen Checkstay Deflector Load', 'tonne', 0, NULL),
    ('mizzen-checkstay-deflector-position', 'Mizzen Checkstay Deflector Position', 'ratio', 0, 1),
    ('mizzen-checkstay-deflector-relative-position', 'Mizzen Checkstay Deflector Relative Position', 'ratio', 0, 1),
    ('mizzen-checkstay-ps-load', 'Mizzen Checkstay Ps Load', 'tonne', 0, NULL),
    ('mizzen-checkstay-sb-load', 'Mizzen Checkstay Sb Load', 'tonne', 0, NULL),
    ('mizzen-cunningham-load', 'Mizzen Cunningham Load', 'tonne', 0, NULL),
    ('mizzen-cunningham-position', 'Mizzen Cunningham Position', 'ratio', 0, 1),
    ('mizzen-cunningham-relative-position', 'Mizzen Cunningham Relative Position', 'ratio', 0, 1),
    ('mizzen-halyard-load', 'Mizzen Halyard Load', 'tonne', 0, NULL),
    ('mizzen-halyard-position', 'Mizzen Halyard Position', 'ratio', 0, 1),
    ('mizzen-halyard-relative-position', 'Mizzen Halyard Relative Position', 'ratio', 0, 1),
    ('mizzen-jib-lock', 'Mizzen Jib Lock', 'bool', 0, 1),
    ('mizzen-jib-overhoist', 'Mizzen Jib Overhoist', 'bool', 0, 1),
    ('mizzen-jib-tack-adjuster-load', 'Mizzen Jib Tack Adjuster Load', 'tonne', 0, NULL),
    ('mizzen-jib-tack-adjuster-position', 'Mizzen Jib Tack Adjuster Position', 'ratio', 0, 1),
    ('mizzen-jib-tack-adjuster-relative-position', 'Mizzen Jib Tack Adjuster Relative Position', 'ratio', 0, 1),
    ('mizzen-outhaul-load', 'Mizzen Outhaul Load', 'tonne', 0, NULL),
    ('mizzen-outhaul-position', 'Mizzen Outhaul Position', 'ratio', 0, 1),
    ('mizzen-outhaul-relative-position', 'Mizzen Outhaul Relative Position', 'ratio', 0, 1),
    ('mizzen-preventer-load', 'Mizzen Preventer Load', 'tonne', 0, NULL),
    ('mizzen-preventer-position', 'Mizzen Preventer Position', 'ratio', 0, 1),
    ('mizzen-preventer-relative-position', 'Mizzen Preventer Relative Position', 'ratio', 0, 1),
    ('mizzen-reef-1-lock', 'Mizzen Reef 1 Lock', 'bool', 0, 1),
    ('mizzen-reef-1-overhoist', 'Mizzen Reef 1 Overhoist', 'bool', 0, 1),
    ('mizzen-reef-2-lock', 'Mizzen Reef 2 Lock', 'bool', 0, 1),
    ('mizzen-reef-2-overhoist', 'Mizzen Reef 2 Overhoist', 'bool', 0, 1),
    ('mizzen-runner-ps-relative-position', 'Mizzen Runner Ps Relative Position', 'ratio', 0, 1),
    ('mizzen-runner-sb-relative-position', 'Mizzen Runner Sb Relative Position', 'ratio', 0, 1),
    ('mizzen-runner-ps-load', 'Mizzen Runner Ps Load', 'tonne', 0, NULL),
    ('mizzen-runner-sb-load', 'Mizzen Runner Sb Load', 'tonne', 0, NULL),
    ('mizzen-sheet-load', 'Mizzen Sheet Load', 'tonne', 0, NULL),
    ('mizzen-sheet-relative-position', 'Mizzen Sheet Relative Position', 'ratio', 0, 1),
    ('mizzen-vang-load', 'Mizzen Vang Load', 'tonne', 0, NULL),
    ('mizzen-vang-position', 'Mizzen Vang Position', 'ratio', 0, 1),
    ('mizzen-vang-relative-position', 'Mizzen Vang Relative Position', 'ratio', 0, 1),
    ('staysail-lock', 'Staysail Lock', 'bool', 0, 1),
    ('staysail-overhoist', 'Staysail Overhoist', 'bool', 0, 1),
    ('staysail-sheet-ps-relative-position', 'Staysail Sheet Ps Relative Position', 'ratio', 0, 1),
    ('staysail-sheet-sb-relative-position', 'Staysail Sheet Sb Relative Position', 'ratio', 0, 1),
    ('staysail-sheet-feeder-ps-load', 'Staysail Sheet Feeder Ps Load', 'tonne', 0, NULL),
    ('staysail-sheet-feeder-sb-load', 'Staysail Sheet Feeder Sb Load', 'tonne', 0, NULL),
    ('staysail-stay-adjuster-load', 'Staysail Stay Adjuster Load', 'tonne', 0, NULL),
    ('staysail-stay-adjuster-position', 'Staysail Stay Adjuster Position', 'ratio', 0, 1),
    ('staysail-stay-adjuster-relative-position', 'Staysail Stay Adjuster Relative Position', 'ratio', 0, 1),
    ('storm-jib-lock', 'Storm Jib Lock', 'bool', 0, 1),
    ('storm-jib-overhoist', 'Storm Jib Overhoist', 'bool', 0, 1);

-- Example reference value for a specific load case
INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT
    'main-sheet-load',
    load_cases.id,
    0.0,
    3.0,
    10.0,
    15.0,
    32.0
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
    'main-checkstay-ps-load',
    load_cases.id,
    5.0,
    6.0,
    10.0,
    14.0,
    15.0
FROM loads.load_cases
JOIN loads.awa_ranges AS awa_range ON load_cases.awa_range_id = awa_range.id
JOIN loads.aws_ranges AS aws_range ON load_cases.aws_range_id = aws_range.id
JOIN loads.sail_sets_combined AS sail_set ON load_cases.sail_set_id = sail_set.id
WHERE awa_range.id = 'upwind' AND aws_range.aws_range = '[15,20)'::numrange
AND sail_set.sails = ARRAY['blade', 'full-main', 'full-mizzen'];

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
