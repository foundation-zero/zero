{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
    "timestamp" TIMESTAMPTZ AS PROCTIME(),
    "data" BYTEA
)
INCLUDE partition AS topic
{{ mqtt_with('amcs/+') }}
