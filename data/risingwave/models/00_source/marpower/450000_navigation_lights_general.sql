{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"NAV_LIGHTS_COMMONALARM"	{{ marpower_struct("BOOLEAN") }},
	"PowerMain_On"	{{ marpower_struct("BOOLEAN") }},
	"PowerEmergency_On"	{{ marpower_struct("BOOLEAN") }},
	"PowerLamps_On"	{{ marpower_struct("BOOLEAN") }},
	"ManualOperation_Active"	{{ marpower_struct("BOOLEAN") }},
	"Communication_Error"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-navigation-lights-general') }}
