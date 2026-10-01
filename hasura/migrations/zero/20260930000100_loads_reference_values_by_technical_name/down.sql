DELETE FROM loads.reference_values;

ALTER TABLE loads.reference_values
    DROP CONSTRAINT reference_values_load_case_id_tack_variable_id_key;

ALTER TABLE loads.reference_values
    DROP COLUMN tack;

ALTER TABLE loads.reference_values
    RENAME COLUMN variable_id TO variable_key;

ALTER TABLE loads.reference_values
    ADD CONSTRAINT reference_values_load_case_id_variable_key_key
    UNIQUE (load_case_id, variable_key);
