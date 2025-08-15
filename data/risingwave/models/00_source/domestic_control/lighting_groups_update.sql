{{ config(materialized='source') }}
CREATE SOURCE {{ this }} (
    "id" TEXT,
    "time" TIMESTAMPTZ as proctime (),
    "level" REAL
)
{{ mqtt_with('domestic/lighting-groups') }}
