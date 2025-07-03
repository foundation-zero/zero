{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	FIRE_DETECT_FAULT	BOOLEAN,
)
{{ mqtt_with('marpower/450000_firedetection') }}
