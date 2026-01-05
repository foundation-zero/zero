{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Status"	{{ marpower_struct("BOOLEAN") }},
	"Ctrl"	{{ marpower_struct("BOOLEAN") }},
	"OpTime"	{{ marpower_struct("BIGINT") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-navigation-lights/#') }}
