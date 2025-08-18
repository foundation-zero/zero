{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"PCS_CB.10_24VDC_EMERG_FAIL"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_24VDC_SERV_FAIL"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_AZI_FOLL_UP_FAIL_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_COM_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_GEAR_OIL_LEV_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_GEAR_OIL_TEMP_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_HYDR_PRESS_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_OIL_LEV_ALARM_SEAL_TANK"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_OVERL_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_OVERSP_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_PITCH_FOLL_UP_FAIL_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"PCS_CB.10_POWER_DISTR_INS"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/150000-pcs/') }}
