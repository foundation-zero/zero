{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	DAS_DETECTION_PERCT	REAL,
	GAS_DETECTION_LVL_SWITCH	BOOLEAN,
)
{{ mqtt_with('marpower/450000_gas_detection') }}
