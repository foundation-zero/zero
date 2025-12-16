{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Opened"	{{ marpower_struct("BOOLEAN") }},
	"Closed"	{{ marpower_struct("BOOLEAN") }},
	"HmiCmdOpen"	{{ marpower_struct("BOOLEAN") }},
	"HmiCmdClose"	{{ marpower_struct("BOOLEAN") }},
	"ShouldBeOpen"	{{ marpower_struct("BOOLEAN") }},
	"HmiControlAvailable"	{{ marpower_struct("BOOLEAN") }},
	"Open"	{{ marpower_struct("BOOLEAN") }},
	"Close"	{{ marpower_struct("BOOLEAN") }},
	"Alarm"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-hvac/#') }}
