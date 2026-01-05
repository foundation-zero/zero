{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"GEN_SERVICE_14E1_01V01_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERVICE_14E1_01V02_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERVICE_14E1_02V01_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERVICE_14E1_02V02_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"EMERGENCY_14E2_VOLTFAULT"	{{ marpower_struct("BOOLEAN") }},
	"EMERGENCY_14E2_ISOFAULT"	{{ marpower_struct("BOOLEAN") }},
	"EMERGENCY_14E2_CONSALARM"	{{ marpower_struct("BOOLEAN") }},
	"EMERGENCY_14E2_TEMPALARM"	{{ marpower_struct("BOOLEAN") }},
	"EMERGENCY_14E2_EMCONS1FAIL"	{{ marpower_struct("BOOLEAN") }},
	"EMERGENCY_14E2_EMCONS2FAIL"	{{ marpower_struct("BOOLEAN") }},
	"GMDSS_14E3_VOLTFAULT"	{{ marpower_struct("BOOLEAN") }},
	"GMDSS_14E3_ISOFAULT"	{{ marpower_struct("BOOLEAN") }},
	"GMDSS_14E3_CHARGERALARM"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERVICE_14E1_ISOFAULT"	{{ marpower_struct("BOOLEAN") }},
	"GEN_SERVICE_14E1_TEMPALARM"	{{ marpower_struct("BOOLEAN") }},
	"EMERG_14E2_VOLTAGE"	{{ marpower_struct("REAL") }},
	"EMERG_14E2_CURRENT"	{{ marpower_struct("REAL") }},
	"GMDSS_14E3_VOLTAGE"	{{ marpower_struct("REAL") }},
	"GMDSS_14E3_CURRENT"	{{ marpower_struct("REAL") }},
	"GMDSS_14E3_EARTHFAULT"	{{ marpower_struct("REAL") }},
	"EMERG_14E2_EARTHFAULT"	{{ marpower_struct("REAL") }},
	"GEN_SERVICE_14E1_EARTHFAULTMON"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-24vdc-system-general') }}
