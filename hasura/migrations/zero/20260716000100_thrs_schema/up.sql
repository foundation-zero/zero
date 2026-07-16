CREATE SCHEMA IF NOT EXISTS thrs;

CREATE TABLE IF NOT EXISTS thrs.machinestate_parameters (
    id SERIAL NOT NULL,
    control_name VARCHAR NOT NULL,
    data_container_name VARCHAR NOT NULL,
    parameters_from VARCHAR,
    parameters_to VARCHAR NOT NULL,
    parameters_diff VARCHAR,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS thrs.machinestate_issue (
    id SERIAL NOT NULL,
    control_name VARCHAR NOT NULL,
    severity_level VARCHAR NOT NULL,
    issue_details VARCHAR,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id)
);

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

CREATE TABLE IF NOT EXISTS thrs.machinestate_event (
    id SERIAL NOT NULL,
    control_name VARCHAR NOT NULL,
    event_name VARCHAR NOT NULL,
    event_details VARCHAR,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (id)
);
