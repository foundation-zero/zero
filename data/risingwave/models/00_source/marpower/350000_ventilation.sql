{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"BATT_VENT_AFT_PS_ON_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"BATT_VENT_AFT_PS_ON_READY"	{{ marpower_struct("BOOLEAN") }},
	"BATT_VENT_AFT_PS_ON_RUN"	{{ marpower_struct("BOOLEAN") }},
	"BATT_VENT_AFT_SB_ON_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"BATT_VENT_AFT_SB_ON_READY"	{{ marpower_struct("BOOLEAN") }},
	"BATT_VENT_AFT_SB_ON_RUN"	{{ marpower_struct("BOOLEAN") }},
	"VENT_EXTR_TECH_SPACE_REM_AVAIL"	{{ marpower_struct("BOOLEAN") }},
	"VENT_EXTR_TECH_SPACE_RUNNING"	{{ marpower_struct("BOOLEAN") }},
	"VENT_SUPP_TECH_SPACE_REM_AVAIL"	{{ marpower_struct("BOOLEAN") }},
	"VENT_SUPP_TECH_SPACE_RUNNING"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/350000-ventilation/') }}
