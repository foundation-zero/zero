{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	ACTIVATE_HULL_TEMP_MEASUREMENT	BOOLEAN,
)
{{ mqtt_with('marpower/amcs_-_ctrl') }}
