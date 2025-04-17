{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	STEER_24V_MONITORING	BOOLEAN,
	STEER_FREQ_DR_POWER_FAIL	BOOLEAN,
	STEER_OIL_FILTER_CLOGGED	BOOLEAN,
	STEER_OIL_LEVEL_TOO_LOW	BOOLEAN,
)
{{ mqtt_with('marpower/xxxx_steering_stystem') }}
