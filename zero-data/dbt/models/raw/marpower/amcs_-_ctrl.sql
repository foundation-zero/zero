{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	ACTIVATE_HULL_TEMP_MEASUREMENT	BOOLEAN,
)
{{ mqtt_with('amcs_-_ctrl') }}