CREATE SCHEMA IF NOT EXISTS thrs;

CREATE TABLE IF NOT EXISTS thrs.machinestate_parameters (
    id SERIAL NOT NULL,
    control_name VARCHAR NOT NULL,
    data_container_name VARCHAR NOT NULL,
    parameters_from JSONB,
    parameters_to JSONB NOT NULL,
    parameters_diff JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_machinestate_parameters_control_timestamp
    ON thrs.machinestate_parameters (control_name, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_machinestate_parameters_container_timestamp
    ON thrs.machinestate_parameters (data_container_name, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_machinestate_parameters_diff
    ON thrs.machinestate_parameters USING GIN (parameters_diff);

CREATE TABLE IF NOT EXISTS thrs.machinestate_issue (
    id SERIAL NOT NULL,
    control_name VARCHAR NOT NULL,
    severity_level VARCHAR NOT NULL,
    issue_details VARCHAR,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_machinestate_issue_control_timestamp
    ON thrs.machinestate_issue (control_name, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_machinestate_issue_severity_timestamp
    ON thrs.machinestate_issue (severity_level, timestamp DESC);

CREATE TABLE IF NOT EXISTS thrs.machinestate_transition (
    id SERIAL NOT NULL,
    control_name VARCHAR NOT NULL,
    trigger_name VARCHAR NOT NULL,
    condition_name VARCHAR NOT NULL,
    state_from VARCHAR NOT NULL,
    state_to VARCHAR NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_machinestate_transition_control_timestamp
    ON thrs.machinestate_transition (control_name, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_machinestate_transition_state_to_timestamp
    ON thrs.machinestate_transition (state_to, timestamp DESC);

CREATE TABLE IF NOT EXISTS thrs.machinestate_event (
    id SERIAL NOT NULL,
    control_name VARCHAR NOT NULL,
    event_name VARCHAR NOT NULL,
    event_details VARCHAR,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_machinestate_event_control_timestamp
    ON thrs.machinestate_event (control_name, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_machinestate_event_name_timestamp
    ON thrs.machinestate_event (event_name, timestamp DESC);

