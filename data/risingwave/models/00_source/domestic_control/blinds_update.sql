{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
    "id" TEXT,
    "time" TIMESTAMPTZ AS proctime (),
    "level" REAL
)
{{ mqtt_with('domestic/blinds') }}
