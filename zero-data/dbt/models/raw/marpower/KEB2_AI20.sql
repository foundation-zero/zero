{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	CHAIN_LOCK_PRESS_SENSOR	REAL,
	BILGE_TANK_PRESS_SENSOR	REAL,
	FLOW_CREW_MESS_HOT_WATER	REAL,
	FLOW_CREW_MESS_COLD_WATER	REAL,
)
{{ mqtt_with('KEB2_AI20') }}