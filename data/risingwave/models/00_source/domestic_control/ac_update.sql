{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
    "id" TEXT,
    "time" TIMESTAMPTZ as proctime (),
    actual_temperature REAL,
    temperature_setpoint REAL,
    actual_humidity REAL,
    humidity_setpoint REAL,
    actual_co2 REAL,
    co2_setpoint REAL,
)
{{ mqtt_with('domestic/ac') }}
