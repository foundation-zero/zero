CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE SCHEMA IF NOT EXISTS loads;


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
    sail_set_id AS id,
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
