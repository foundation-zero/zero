{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"COOL_PMP1_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"COOL_PMP1_REMOTE"	{{ marpower_struct("BOOLEAN") }},
	"VACUUMALARM"	{{ marpower_struct("BOOLEAN") }},
	"FLOW"	{{ marpower_struct("REAL") }},
	"COOL_PMP1_STARTSTOP"	{{ marpower_struct("BOOLEAN") }},
	"COOL_PMP2_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"COOL_PMP2_REMOTE"	{{ marpower_struct("BOOLEAN") }},
	"COOL_PMP2_STARTSTOP"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/380000-seawater') }}
