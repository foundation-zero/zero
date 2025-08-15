{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
    "id" TEXT,
    "time" TIMESTAMPTZ as proctime (),
    "level" REAL
)
{{ mqtt_with('domestic/blinds') }}
