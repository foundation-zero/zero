CREATE schema IF NOT EXISTS thrs;

DROP TABLE IF EXISTS thrs.machinestate_parameters CASCADE;
CREATE TABLE thrs.machinestate_parameters (
        id SERIAL NOT NULL, 
        control_name VARCHAR NOT NULL, 
        data_container_name VARCHAR NOT NULL, 
        parameters_from VARCHAR, 
        parameters_to VARCHAR NOT NULL, 
        parameters_diff VARCHAR, 
        timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
        PRIMARY KEY (id)
);




DROP TABLE IF EXISTS thrs.machinestate_issue CASCADE;
CREATE TABLE thrs.machinestate_issue (
        id SERIAL NOT NULL, 
        control_name VARCHAR NOT NULL, 
        severity_level severity NOT NULL, 
        issue_details VARCHAR, 
        timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
        PRIMARY KEY (id)
);



DROP TABLE IF EXISTS thrs.machinestate_transition CASCADE;
CREATE TABLE thrs.machinestate_transition (
        id SERIAL NOT NULL, 
        control_name VARCHAR NOT NULL, 
        trigger_name VARCHAR NOT NULL, 
        condition_name VARCHAR NOT NULL, 
        state_from VARCHAR NOT NULL, 
        state_to VARCHAR NOT NULL, 
        timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
        PRIMARY KEY (id)
);



DROP TABLE IF EXISTS thrs.machinestate_event CASCADE;       
CREATE TABLE thrs.machinestate_event (
        id SERIAL NOT NULL, 
        control_name VARCHAR NOT NULL, 
        event_name VARCHAR NOT NULL, 
        event_details VARCHAR, 
        timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
        PRIMARY KEY (id)
);
