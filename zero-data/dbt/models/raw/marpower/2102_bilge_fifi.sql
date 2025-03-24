{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	BILGE_LEVEL_SUB_PUMP3_ALARM	BOOLEAN,
)
{{ mqtt_with('2102_bilge_fifi') }}