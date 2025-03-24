{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	PNEUMATIC_PRESSURE	REAL,
)
{{ mqtt_with('2900_pneumatic_') }}