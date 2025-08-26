{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"CHAIN_LOCK_PUMP_REM_AVAIL"	{{ marpower_struct("BOOLEAN") }},
	"CHAIN_LOCK_PUMP_RUNNING"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/210000-bilge-fifi/chpump') }}
