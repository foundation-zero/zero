{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	BILGE_LEVEL_SUB_PUMP3_ALARM	BOOLEAN,
)
{{ mqtt_with('marpower/2102_bilge_fifi') }}
