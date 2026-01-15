{{ config(materialized='source') }}
CREATE SOURCE {{ this }} (
    "id" TEXT,
    "time" TIMESTAMPTZ AS proctime (),
    "is_on" BOOLEAN
)
{{ mqtt_with('domestic/amplifiers') }}
