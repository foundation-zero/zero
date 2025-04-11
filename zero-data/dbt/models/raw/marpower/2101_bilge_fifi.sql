{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	BILGE_LEVEL_SUB_PUMP2_ALARM	BOOLEAN,
	BILGE_TANK_PRESS_SENSOR	REAL,
)
{{ mqtt_with('marpower/2101_bilge_fifi') }}
