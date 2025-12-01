CREATE SCHEMA IF NOT EXISTS loads;

DROP TYPE IF EXISTS unit CASCADE;
CREATE TYPE unit AS ENUM ('tonne');

DROP TABLE IF EXISTS loads.sails CASCADE;
CREATE TABLE loads.sails (
    id TEXT PRIMARY KEY,             
    abbreviation TEXT NOT NULL,               
    position_id TEXT NOT NULL,       
    name TEXT NOT NULL              
);

DROP TABLE IF EXISTS loads.sail_sets CASCADE;
CREATE TABLE loads.sail_sets (
    id SERIAL PRIMARY KEY,
    main_sail_id TEXT REFERENCES loads.sails(id),
    mizzen_sail_id TEXT REFERENCES loads.sails(id), 
    fore_inner_sail_id TEXT REFERENCES loads.sails(id),
    fore_outer_sail_id TEXT REFERENCES loads.sails(id),
    mizzen_fore_sail_id TEXT REFERENCES loads.sails(id),
    sail_set TEXT[] GENERATED ALWAYS AS (
        ARRAY_REMOVE(ARRAY[main_sail_id, mizzen_sail_id, fore_inner_sail_id, fore_outer_sail_id, mizzen_fore_sail_id], NULL)
    ) STORED,
    UNIQUE(main_sail_id, mizzen_sail_id, fore_inner_sail_id, fore_outer_sail_id, mizzen_fore_sail_id)
);

DROP TABLE IF EXISTS loads.twa_ranges CASCADE;
CREATE TABLE loads.twa_ranges (
  id SERIAL PRIMARY KEY,
  twa numrange NOT NULL CHECK (lower(twa) >= 0 AND upper(twa) <= 180)
);

DROP TABLE IF EXISTS loads.tws_ranges CASCADE;
CREATE TABLE loads.tws_ranges (
  id SERIAL PRIMARY KEY,
  tws numrange NOT NULL CHECK (lower(tws) >= 0)
);

DROP TABLE IF EXISTS loads.load_cases CASCADE;
CREATE TABLE loads.load_cases (
  id SERIAL PRIMARY KEY,
  twa_range_id INTEGER NOT NULL REFERENCES loads.twa_ranges(id) ON DELETE RESTRICT,
  tws_range_id INTEGER NOT NULL REFERENCES loads.tws_ranges(id) ON DELETE RESTRICT,
  sail_set_id INTEGER NOT NULL REFERENCES loads.sail_sets(id) ON DELETE RESTRICT,
  -- Future extensions:
  -- sea_state_id INTEGER REFERENCES loads.sea_states(id),
  -- propulsion_mode_id INTEGER REFERENCES loads.propulsion_modes(id),
  UNIQUE(twa_range_id, tws_range_id, sail_set_id)
);

DROP TABLE IF EXISTS loads.variables CASCADE;
CREATE TABLE loads.variables (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  unit unit NOT NULL
);

DROP TABLE IF EXISTS loads.reference_values CASCADE;
CREATE TABLE loads.reference_values (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  load_case_id INTEGER NOT NULL REFERENCES loads.load_cases(id) ON DELETE RESTRICT,
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
WITH main_sails AS (
    SELECT id FROM loads.sails WHERE position_id = 'main'
    UNION ALL
    SELECT NULL
),
mizzen_sails AS (
    SELECT id FROM loads.sails WHERE position_id = 'mizzen'
    UNION ALL
    SELECT NULL
),
mizzen_fore_sails AS (
    SELECT id FROM loads.sails WHERE position_id = 'mizzen-fore'
    UNION ALL
    SELECT NULL
),
fore_inner_sails AS (
    SELECT id FROM loads.sails WHERE position_id = 'fore-inner'
    UNION ALL
    SELECT NULL
),
fore_outer_sails AS (
    SELECT id FROM loads.sails WHERE position_id = 'fore-outer'
    UNION ALL
    SELECT NULL
)
INSERT INTO loads.sail_sets (main_sail_id, mizzen_sail_id, fore_inner_sail_id, fore_outer_sail_id, mizzen_fore_sail_id)
SELECT 
    main_sail.id,
    mizzen_sail.id,
    fore_inner_sail.id,
    fore_outer_sail.id,
    mizzen_fore_sail.id
FROM main_sails AS main_sail
CROSS JOIN mizzen_sails AS mizzen_sail
CROSS JOIN fore_inner_sails AS fore_inner_sail
CROSS JOIN fore_outer_sails AS fore_outer_sail
CROSS JOIN mizzen_fore_sails AS mizzen_fore_sail;

-- Define TWA ranges
INSERT INTO loads.twa_ranges (twa) VALUES
  ('[0,40)'),
  ('[40,50)'),
  ('[50,60)'),
  ('[60,90)'),
  ('[90,120)'),
  ('[120,150)'),
  ('[150,180]');

-- Define TWS ranges
INSERT INTO loads.tws_ranges (tws) VALUES
  ('[0,10)'),
  ('[10,15)'),
  ('[15,20)'),
  ('[20,25)'),
  ('[25,30)'),
  ('[30,40)'),
  ('[40,50)'),
  ('[50,)');

INSERT INTO loads.load_cases (twa_range_id, tws_range_id, sail_set_id)
SELECT 
    twa_range.id AS twa_range_id,
    tws_range.id AS tws_range_id,
    sail_set.id AS sail_set_id
FROM loads.twa_ranges AS twa_range
CROSS JOIN loads.tws_ranges AS tws_range
CROSS JOIN loads.sail_sets AS sail_set;

-- Define variables
INSERT INTO loads.variables (id, name, unit) VALUES
  ('headstay-load', 'Headstay Load', 'tonne');

-- Example reference value for a specific load case
INSERT INTO loads.reference_values (variable_id, load_case_id, alarm_low, warning_low, target, warning_high, alarm_high)
SELECT 
    'headstay-load',
    load_cases.id,
    NULL,
    NULL,
    10.0,
    NULL,
    NULL
FROM loads.load_cases
JOIN loads.twa_ranges AS twa_range ON load_cases.twa_range_id = twa_range.id
JOIN loads.tws_ranges AS tws_range ON load_cases.tws_range_id = tws_range.id
JOIN loads.sail_sets AS sail_set ON load_cases.sail_set_id = sail_set.id
WHERE twa_range.twa = '[40,50)'::numrange AND tws_range.tws = '[15,20)'::numrange
AND sail_set.sail_set = ARRAY['full-main', 'full-mizzen', 'blade'];