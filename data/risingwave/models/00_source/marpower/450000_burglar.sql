{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"206U01_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"206U02_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"206U03_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"ALARM_SYSTEM_ONOFF"	{{ marpower_struct("BOOLEAN") }},
	"206U04_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"206U05_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"206U06_ALARM"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-burglar') }}
