{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"GEN_SERV_PUMP2_FIELD_START"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERV_PUMP2_FIELD_STOP"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERV_PUMP2_REM_AVAIL"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/210000-bilge-fifi/servpump2') }}
