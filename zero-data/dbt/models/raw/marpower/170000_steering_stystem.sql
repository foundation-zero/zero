{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	STEER_FREQ_DR_FAIL	BOOLEAN,
)
{{ mqtt_with('marpower/170000_steering_stystem') }}
