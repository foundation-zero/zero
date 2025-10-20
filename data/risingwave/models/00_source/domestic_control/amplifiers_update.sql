{{ config(materialized='source') }}
CREATE TABLE {{ this }} (
    "id" TEXT,
    "time" TIMESTAMPTZ as proctime (),
    "is_on" BOOLEAN
)
{{ mqtt_with('domestic/amplifiers') }}
