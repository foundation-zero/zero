{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"TRANS_PUMP_BLCK_WAT_REMAVAIL"	{{ marpower_struct("BOOLEAN") }},
	"TRANS_PUMP_BLCK_WAT_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"TRANS_PUMP_GREY_WAT_REMAVAIL"	{{ marpower_struct("BOOLEAN") }},
	"TRANS_PUMP_GREY_WAT_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"PUMP_FWD_GREY_WAT_REMAVAIL"	{{ marpower_struct("BOOLEAN") }},
	"PUMP_FWD_GREY_WAT_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"TREAT_RELEASE"	{{ marpower_struct("BOOLEAN") }},
	"TREAT_GEN_WARNING_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"SEWAGE_TREATMENT_PLANT_GENERAL_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"TREAT_DRYRUNNPROT"	{{ marpower_struct("BOOLEAN") }},
	"SEWAGE_TREATMENT_PLANT_ON"	{{ marpower_struct("BOOLEAN") }},
	"GREY_WATER_TANK_AFT_SB_LEVEL"	{{ marpower_struct("REAL") }},
	"BLACK_GREY_WATER_TANK_AFT_PS_LEVEL"	{{ marpower_struct("REAL") }},
	"SLUDGE_TANK_PS_LEVEL"	{{ marpower_struct("REAL") }},
	"TREAT_HOLDING_TANK_LEVEL"	{{ marpower_struct("REAL") }},
	"TREAT_SLUDGE_TANK_LEVEL"	{{ marpower_struct("REAL") }},
	"TRANS_PUMP_BLCK_WAT_STARTSTOP"	{{ marpower_struct("BOOLEAN") }},
	"TRANS_PUMP_GREY_WAT_STARTSTOP"	{{ marpower_struct("BOOLEAN") }},
	"PUMP_FWD_GREY_WAT_STARTSTOP"	{{ marpower_struct("BOOLEAN") }},
	"GREY_WATER_TANK_FWD_SB_LEVEL"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/340000-sewage') }}
