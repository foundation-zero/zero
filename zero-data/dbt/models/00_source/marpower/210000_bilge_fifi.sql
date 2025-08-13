{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"BILGE_BATT_COMP_5_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"BILGE_BATT_COMP_6_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"BILGE_FRAME53_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"BILGE_FRAME68_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"BILGE_TANK_PRESS_SENSOR"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/210000-bilge-fifi/') }}
