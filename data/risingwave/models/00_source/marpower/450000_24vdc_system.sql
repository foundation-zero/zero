{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"DB_EMERGENCY_14E2_CONS_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"DB_EMERGENCY_14E2_EM_CONS1_FAIL"	{{ marpower_struct("BOOLEAN") }},
	"DB_EMERGENCY_14E2_EM_CONS2_FAIL"	{{ marpower_struct("BOOLEAN") }},
	"DB_EMERGENCY_14E2_ISOLATION_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DB_EMERGENCY_14E2_TEMP_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"DB_EMERGENCY_14E2_VOLT_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DB_EMERG_14E2_CURRENT"	{{ marpower_struct("REAL") }},
	"DB_EMERG_14E2_EARTH_FAULT_MON"	{{ marpower_struct("REAL") }},
	"DB_EMERG_14E2_VOLTAGE"	{{ marpower_struct("REAL") }},
	"DB_GEN_SERVICE_14E1_01V01_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DB_GEN_SERVICE_14E1_01V02_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DB_GEN_SERVICE_14E1_02V01_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DB_GEN_SERVICE_14E1_02V02_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DB_GEN_SERVICE_14E1_EARTH_FAULT_MON"	{{ marpower_struct("REAL") }},
	"DB_GEN_SERVICE_14E1_ISOLATION_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DB_GEN_SERVICE_14E1_TEMP_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"DB_GMDSS_14E3_CHARGER_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"DB_GMDSS_14E3_CURRENT"	{{ marpower_struct("REAL") }},
	"DB_GMDSS_14E3_ISOLATION_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DB_GMDSS_14E3_VOLTAGE"	{{ marpower_struct("REAL") }},
	"DB_GMDSS_14E3_VOLT_FAULT"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-24vdc-system/') }}
