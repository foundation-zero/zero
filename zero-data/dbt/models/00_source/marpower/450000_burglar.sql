{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"BURGLAR_ALARM_206U01"	{{ marpower_struct("BOOLEAN") }},
	"BURGLAR_ALARM_206U02"	{{ marpower_struct("BOOLEAN") }},
	"BURGLAR_ALARM_206U03"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-burglar/') }}
