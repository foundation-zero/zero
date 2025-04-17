{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	DECK_CRANE_GEN_ALARM	BOOLEAN,
	GUEST_TENDER_HATCH_CL_LOCK	BOOLEAN,
	MOB_TENDER_HATCH_CL_LOCK	BOOLEAN,
)
{{ mqtt_with('marpower/7500_deck_crane') }}
