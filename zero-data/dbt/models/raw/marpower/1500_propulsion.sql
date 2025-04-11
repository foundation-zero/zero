{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	BOW_THRUST_BEARING_TEMP_DE	REAL,
	BOW_THRUST_BEARING_TEMP_NDE	REAL,
	STERN_THRUST_BEARING_TEMP_DE	REAL,
	STERN_THRUST_BEARING_TEMP_NDE	REAL,
)
{{ mqtt_with('marpower/1500_propulsion') }}
