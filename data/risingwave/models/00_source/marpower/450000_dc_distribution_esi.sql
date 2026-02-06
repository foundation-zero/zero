{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ONLINE"	{{ marpower_struct("BOOLEAN") }},
	"AVAILABLE"	{{ marpower_struct("BOOLEAN") }},
	"ERROR"	{{ marpower_struct("BOOLEAN") }},
	"OVERLOAD"	{{ marpower_struct("BOOLEAN") }},
	"EMERGSWITCHOFF1"	{{ marpower_struct("BOOLEAN") }},
	"EMERGSWITCHOFF2"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-dc-distribution/esi/#') }}
