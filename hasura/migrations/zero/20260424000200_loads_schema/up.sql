CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE SCHEMA IF NOT EXISTS loads;


CREATE TABLE loads.sail_positions (
    id TEXT PRIMARY KEY
);

CREATE TABLE loads.sails (
    id TEXT PRIMARY KEY,
    abbreviation TEXT NOT NULL,
    position_id TEXT NOT NULL REFERENCES loads.sail_positions(id),
    name TEXT NOT NULL,
    variant_name TEXT NOT NULL
);

CREATE TABLE loads.sail_sets (
    sail_set_id INTEGER NOT NULL,
    position_id TEXT NOT NULL REFERENCES loads.sail_positions(id),
    sail_id TEXT REFERENCES loads.sails(id)
);

CREATE OR REPLACE VIEW loads.sail_sets_combined AS
-- This view makes looking up the sail case easier by aggregating the sails into an array
-- Lookup can be done by matching the (ordered) array of sails
SELECT
    sail_set_id AS id,
    ARRAY_AGG(sail_id ORDER BY sail_id) FILTER (WHERE sail_id IS NOT NULL) AS sails
FROM loads.sail_sets
GROUP BY sail_set_id;

CREATE TABLE loads.awa_ranges (
    id TEXT PRIMARY KEY,
    awa_range numrange NOT NULL CHECK (lower(awa_range) >= 0 AND upper(awa_range) <= 180),
    EXCLUDE USING gist (awa_range WITH &&)
);

CREATE TABLE loads.aws_ranges (
    id SERIAL PRIMARY KEY,
    aws_range numrange NOT NULL CHECK (lower(aws_range) >= 0),
    EXCLUDE USING gist (aws_range WITH &&)
);

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

CREATE TABLE loads.reference_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    load_case_id UUID NOT NULL REFERENCES loads.load_cases(id) ON DELETE RESTRICT,
    variable_key TEXT NOT NULL,
    alarm_low NUMERIC,
    warning_low NUMERIC,
    target NUMERIC,
    warning_high NUMERIC,
    alarm_high NUMERIC,
    UNIQUE(load_case_id, variable_key),
    CHECK (
        (alarm_low IS NULL OR warning_low IS NULL OR alarm_low <= warning_low) AND
        (warning_low IS NULL OR target IS NULL OR warning_low <= target) AND
        (warning_high IS NULL OR target IS NULL OR target <= warning_high) AND
        (warning_high IS NULL OR alarm_high IS NULL OR warning_high <= alarm_high)
    )
);
