{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"UmsEntranceUnitMannedSwitch"	{{ marpower_struct("BOOLEAN") }},
	"UmsEntranceUnitUnmannedSwitch"	{{ marpower_struct("BOOLEAN") }},
	"UmsEntranceUnitOneManSwitch"	{{ marpower_struct("BOOLEAN") }},
	"UmsEntranceUnitMoreMenSwitch"	{{ marpower_struct("BOOLEAN") }},
	"UmsOneManTimerResetButton"	{{ marpower_struct("BOOLEAN") }},
	"UmsMannedLight"	{{ marpower_struct("BOOLEAN") }},
	"UmsTimingOnLight"	{{ marpower_struct("BOOLEAN") }},
	"UmsOneManTimerResetLight"	{{ marpower_struct("BOOLEAN") }},
	"UmsCabin1Buzzer"	{{ marpower_struct("BOOLEAN") }},
	"UmsCabin2Buzzer"	{{ marpower_struct("BOOLEAN") }},
	"UmsCabin3Buzzer"	{{ marpower_struct("BOOLEAN") }},
	"UMSCabin1Duty"	{{ marpower_struct("BOOLEAN") }},
	"UMSCabin1AlarmLed"	{{ marpower_struct("BOOLEAN") }},
	"UMSCabin2Duty"	{{ marpower_struct("BOOLEAN") }},
	"UMSCabin2AlarmLed"	{{ marpower_struct("BOOLEAN") }},
	"UMSCabin3Duty"	{{ marpower_struct("BOOLEAN") }},
	"UMSCabin3AlarmLed"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-amcs/ums') }}
