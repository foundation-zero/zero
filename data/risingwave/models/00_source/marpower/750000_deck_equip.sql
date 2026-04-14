{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"PASS_HATCH_CL_LOCK"	{{ marpower_struct("BOOLEAN") }},
	"SBL_SB_CLOSED_LOCKED"	{{ marpower_struct("BOOLEAN") }},
	"DECK_CRANE_GENALARM"	{{ marpower_struct("BOOLEAN") }},
	"MOB_TENDER_HATCH_CL_LOCK"	{{ marpower_struct("BOOLEAN") }},
	"GUEST_TENDER_HATCH_CL_LOCK"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/750000-deck-equip') }}
