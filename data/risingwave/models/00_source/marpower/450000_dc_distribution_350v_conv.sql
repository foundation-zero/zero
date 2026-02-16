{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"OPERATINGVOLTPRESENT"	{{ marpower_struct("BOOLEAN") }},
	"BUSVOLTPRESENT"	{{ marpower_struct("BOOLEAN") }},
	"ISOLATIONWARNING"	{{ marpower_struct("BOOLEAN") }},
	"ISOLATIONFAULT"	{{ marpower_struct("BOOLEAN") }},
	"ISOLATIONDISABLED"	{{ marpower_struct("BOOLEAN") }},
	"AUXPOWER700TO24VDCFAILURE"	{{ marpower_struct("BOOLEAN") }},
	"AUXPOWER24TO24VDCFAILURE"	{{ marpower_struct("BOOLEAN") }},
	"DISABLEISOLATION"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-dc-distribution/350v-conv/#') }}
