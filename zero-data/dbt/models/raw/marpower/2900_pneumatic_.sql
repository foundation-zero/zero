{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	PNEUMATIC_PRESSURE	REAL,
)
{{ mqtt_with('marpower/2900_pneumatic_') }}
