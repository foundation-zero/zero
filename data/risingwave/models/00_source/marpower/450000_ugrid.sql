{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ENABLE"	{{ marpower_struct("BOOLEAN") }},
	"ENABLEFIRMWARE"	{{ marpower_struct("BOOLEAN") }},
	"DIGOUT1"	{{ marpower_struct("BOOLEAN") }},
	"DIGOUT2"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-ugrid/#') }}
