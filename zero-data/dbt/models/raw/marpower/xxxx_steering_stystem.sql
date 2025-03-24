{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	STEER_OIL_LEVEL_TOO_LOW	BOOLEAN,
	STEER_OIL_FILTER_CLOGGED	BOOLEAN,
	STEER_24V_MONITORING	BOOLEAN,
	STEER_FREQ_DR_POWER_FAIL	BOOLEAN,
)
{{ mqtt_with('xxxx_steering_stystem') }}