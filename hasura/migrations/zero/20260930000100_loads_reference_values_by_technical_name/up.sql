-- Rows keyed by variable key cannot be mapped to a technical name and tack; re-apply loads_reference_values.sql after migrating.
DELETE FROM loads.reference_values;

ALTER TABLE loads.reference_values
    DROP CONSTRAINT reference_values_load_case_id_variable_key_key;

ALTER TABLE loads.reference_values
    RENAME COLUMN variable_key TO variable_id;

ALTER TABLE loads.reference_values
    ADD COLUMN tack TEXT NOT NULL CHECK (tack IN ('port', 'starboard'));

ALTER TABLE loads.reference_values
    ADD CONSTRAINT reference_values_load_case_id_tack_variable_id_key
    UNIQUE (load_case_id, tack, variable_id);
