{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TECH_WAT_SALINITY	REAL,
	TECH_WAT_TANK1_LEVEL	REAL,
	TECH_WAT_TANK2_LEVEL	REAL,
	TECH_WAT_FLOW_CHARCOAL_FILTER_B01	REAL,
)
{{ mqtt_with('KEB1_AI28') }}