{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"alarm"	{{ marpower_struct("BOOLEAN") }},
	"prealarm"	{{ marpower_struct("BOOLEAN") }},
	"fault"	{{ marpower_struct("BOOLEAN") }},
	"disabled"	{{ marpower_struct("BOOLEAN") }},
	"test"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-firedetection/#') }}
