-- Rows keyed by variable key cannot be mapped to a technical name and tack; re-apply loads_reference_values.sql after migrating.
DELETE FROM loads.reference_values;

-- Databases created before #423 still have variable_id from the original loads_schema migration;
-- databases created after it have variable_key. Handle both.
ALTER TABLE loads.reference_values
    DROP CONSTRAINT IF EXISTS reference_values_load_case_id_variable_key_key;

ALTER TABLE loads.reference_values
    DROP CONSTRAINT IF EXISTS reference_values_load_case_id_variable_id_key;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'loads' AND table_name = 'reference_values' AND column_name = 'variable_key'
    ) THEN
        ALTER TABLE loads.reference_values RENAME COLUMN variable_key TO variable_id;
    END IF;
END $$;

ALTER TABLE loads.reference_values
    ADD COLUMN tack TEXT NOT NULL CHECK (tack IN ('port', 'starboard'));

ALTER TABLE loads.reference_values
    ADD CONSTRAINT reference_values_load_case_id_tack_variable_id_key
    UNIQUE (load_case_id, tack, variable_id);
