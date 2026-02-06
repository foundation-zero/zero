{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Voltage"	{{ marpower_struct("REAL") }},
	"Current"	{{ marpower_struct("REAL") }},
	"Power"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-24vdc-system/conv/#') }}
