{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"LEVEL_BLACK_GREY_WATER_TANK_AFT_PS"	{{ marpower_struct("REAL") }},
	"LEVEL_GREY_WATER_TANK_AFT_SB"	{{ marpower_struct("REAL") }},
	"LEVEL_SLUDGE_TANK_PS"	{{ marpower_struct("REAL") }},
	"PUMP_FWD_GREY_WAT_REM_AVAIL"	{{ marpower_struct("BOOLEAN") }},
	"PUMP_FWD_GREY_WAT_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"SEW_TREAT_DRY_RUNN_PROT"	{{ marpower_struct("BOOLEAN") }},
	"SEW_TREAT_GEN_WARNING_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"SEW_TREAT_RELEASE"	{{ marpower_struct("BOOLEAN") }},
	"Sewage_Treatment_Plant_General_Alarm"	{{ marpower_struct("BOOLEAN") }},
	"Sewage_Treatment_Plant_On"	{{ marpower_struct("BOOLEAN") }},
	"TRANS_PUMP_BLCK_WAT_REM_AVAIL"	{{ marpower_struct("BOOLEAN") }},
	"TRANS_PUMP_BLCK_WAT_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"TRANS_PUMP_GREY_WAT_REM_AVAIL"	{{ marpower_struct("BOOLEAN") }},
	"TRANS_PUMP_GREY_WAT_RUNNING"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/340000-sewage/') }}
