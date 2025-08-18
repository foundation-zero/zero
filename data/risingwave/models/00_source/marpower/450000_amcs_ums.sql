{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"UmsEntranceUnitMannedSwitch"	{{ marpower_struct("BOOLEAN") }},
	"UmsEntranceUnitMoreMenSwitch"	{{ marpower_struct("BOOLEAN") }},
	"UmsEntranceUnitOneManSwitch"	{{ marpower_struct("BOOLEAN") }},
	"UmsEntranceUnitUnmannedSwitch"	{{ marpower_struct("BOOLEAN") }},
	"UmsMannedLight"	{{ marpower_struct("BOOLEAN") }},
	"UmsOneManTimerResetButton"	{{ marpower_struct("BOOLEAN") }},
	"UmsOneManTimerResetLight"	{{ marpower_struct("BOOLEAN") }},
	"UmsTimingOnLight"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-amcs/ums') }}
