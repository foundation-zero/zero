{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	FIRE_DETECT_FAULT	BOOLEAN,
)
{{ mqtt_with('4500_firedetection') }}