{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	DECK_CRANE_GEN_ALARM	BOOLEAN,
	MOB_TENDER_HATCH_CL_LOCK	BOOLEAN,
	GUEST_TENDER_HATCH_CL_LOCK	BOOLEAN,
)
{{ mqtt_with('7500_deck_crane') }}