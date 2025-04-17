{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	SBL_SB_CLOSED_LOCKED	BOOLEAN,
	SBL_SPARE_INPUT	BOOLEAN,
)
{{ mqtt_with('marpower/7500_boarding_ladder') }}
