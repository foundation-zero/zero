{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ACC_SENSOR_2_OUTPX"	{{ marpower_struct("REAL") }},
	"ACC_SENSOR_2_OUTPY"	{{ marpower_struct("REAL") }},
	"ACC_SENSOR_2_OUTPZ"	{{ marpower_struct("REAL") }},
	"HELM_PS_BACKLIGHT_UP_DOWN"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_CREW_CALL"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_MUTE_AMCS"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-amcs/') }}
