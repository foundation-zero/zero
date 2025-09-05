{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"STERN_THRUST_BEARING_TEMP_DE"	{{ marpower_struct("REAL") }},
	"STERN_THRUST_BEARING_TEMP_NDE"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/150000-propulsion/') }}
