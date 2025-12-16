{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"GFDEnabled"	{{ marpower_struct("BOOLEAN") }},
	"FieldVoltageAvailable"	{{ marpower_struct("BOOLEAN") }},
	"PA24V"	{{ marpower_struct("BOOLEAN") }},
	"MA24V"	{{ marpower_struct("BOOLEAN") }},
	"PA0V"	{{ marpower_struct("BOOLEAN") }},
	"MA0V"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-dc-distribution/pwr/#') }}
