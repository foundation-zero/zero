{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"OILLEVELTOOLOW"	{{ marpower_struct("BOOLEAN") }},
	"OILFILTERCLOGGED"	{{ marpower_struct("BOOLEAN") }},
	"24VMONITORING"	{{ marpower_struct("BOOLEAN") }},
	"FREQ_DR_POWERFAIL"	{{ marpower_struct("BOOLEAN") }},
	"FREQ_DR_FAIL"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/170000-steering-system') }}
