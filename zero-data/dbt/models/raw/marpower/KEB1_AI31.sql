{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	STERN_THRUST_BEARING_TEMP_DE	REAL,
	STERN_THRUST_BEARING_TEMP_NDE	REAL,
)
{{ mqtt_with('KEB1_AI31') }}