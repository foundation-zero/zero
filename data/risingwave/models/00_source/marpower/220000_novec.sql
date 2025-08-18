{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"NOVEC_PRESSURE_SWITCH1"	{{ marpower_struct("BOOLEAN") }},
	"NOVEC_PRESSURE_SWITCH2"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/220000-novec/') }}
