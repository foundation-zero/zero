{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"SEA_WATER_COOL_PMP1_REMOTE"	{{ marpower_struct("BOOLEAN") }},
	"SEA_WATER_COOL_PMP1_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"SEA_WATER_FLOW_IN"	{{ marpower_struct("REAL") }},
	"SEA_WATER_FLOW_OUT"	{{ marpower_struct("REAL") }},
	"SEA_WATER_VACUUM_ALARM"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/380000-seawater/') }}
