{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"STATUSOK"	{{ marpower_struct("BOOLEAN") }},
	"TEMPWARN1"	{{ marpower_struct("BOOLEAN") }},
	"TEMPWARN2"	{{ marpower_struct("BOOLEAN") }},
	"ENABLEDISABLE"	{{ marpower_struct("BOOLEAN") }},
	"SAFETYDISCONNECT"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-dc-distribution/conv/#') }}
