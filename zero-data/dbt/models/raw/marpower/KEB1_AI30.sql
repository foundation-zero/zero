{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TECH_WAT_FLOW_ADIABATIC_COOL_B08	REAL,
	TECH_WAT_FLOW_ADIABATIC_COOL_B09	REAL,
)
{{ mqtt_with('KEB1_AI30') }}