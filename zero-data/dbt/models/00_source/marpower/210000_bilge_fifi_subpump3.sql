{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"BILGE_LEVEL_SUB_PUMP3_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"SUBMERS_PUMP3_REM_AVAIL"	{{ marpower_struct("BOOLEAN") }},
	"SUBMERS_PUMP3_RUNNING"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/210000-bilge-fifi/subpump3') }}
