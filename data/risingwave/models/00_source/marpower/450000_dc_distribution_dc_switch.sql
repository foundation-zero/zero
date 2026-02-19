{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"OPENED"	{{ marpower_struct("BOOLEAN") }},
	"CLOSED"	{{ marpower_struct("BOOLEAN") }},
	"TRIPPED"	{{ marpower_struct("BOOLEAN") }},
	"RESET"	{{ marpower_struct("BOOLEAN") }},
	"OPEN"	{{ marpower_struct("BOOLEAN") }},
	"CLOSE"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-dc-distribution/dc-switch/#') }}
