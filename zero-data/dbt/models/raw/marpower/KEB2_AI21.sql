{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	FLOW_GALLEY_1_HOT_WATER	REAL,
	FLOW_GALLEY_1_COLD_WATER	REAL,
	FLOW_GALLEY_2_HOT_WATER	REAL,
	FLOW_GALLEY_2_COLD_WATER	REAL,
)
{{ mqtt_with('KEB2_AI21') }}