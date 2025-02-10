{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	BATT_VENT_AFT_PS_SPEED	BOOLEAN,
	BATT_VENT_FWD_SB_SPEED	BOOLEAN,
)
{{ mqtt_with('KEB2_AO60') }}