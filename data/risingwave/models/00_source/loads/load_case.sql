{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
    sea_state TEXT,
    awa FLOAT,
    aws FLOAT,
    pcs_mode STRUCT<
        fwd VARCHAR,
        aft VARCHAR
    >,
    sails TEXT[],
    "time" TIMESTAMPTZ as proctime ()
)
{{ mqtt_with('loads/control/case') }}
