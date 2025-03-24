{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	SBL_SB_CLOSED_LOCKED	BOOLEAN,
	SBL_SPARE_INPUT	BOOLEAN,
)
{{ mqtt_with('7500_boarding_ladder') }}