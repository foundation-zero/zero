{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"PRESSURE_SWITCH1_ACTIVE"	{{ marpower_struct("BOOLEAN") }},
	"PRESSURE_SWITCH2_ACTIVE"	{{ marpower_struct("BOOLEAN") }},
	"RELEASEDALARM"	{{ marpower_struct("BOOLEAN") }},
	"BREAKERTRIPPEDALARM"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/220000-novec') }}
