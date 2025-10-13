{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Voltage_A"	{{ marpower_struct("REAL") }},
	"Voltage_B"	{{ marpower_struct("REAL") }},
	"Current_A"	{{ marpower_struct("REAL") }},
	"Current_B"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/battery-dc-converter/#') }}
