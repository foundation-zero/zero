{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"x_RcAnchrRunning"	BOOLEAN,
	"x_RcAnchrEstop"	BOOLEAN,
	"x_RcCrwsNstRunning"	BOOLEAN,
	"x_RcCrwsNstEstop"	BOOLEAN,
	"x_RcDrumRunning"	BOOLEAN,
	"x_RcDrumEstop"	BOOLEAN,
	"x_RcHeadRunning"	BOOLEAN,
	"x_RcHeadEstop"	BOOLEAN,
	"x_RcMainRunning"	BOOLEAN,
	"x_RcMainEstop"	BOOLEAN,
	"x_RcMntncRunning"	BOOLEAN,
	"x_RcMntncEstop"	BOOLEAN,
	"x_RcMzznRunning"	BOOLEAN,
	"x_RcMzznEstop"	BOOLEAN,
	"x_Spare1Running"	BOOLEAN,
	"x_Spare1Estop"	BOOLEAN,
	"x_Spare2Running"	BOOLEAN,
	"x_Spare2Estop"	BOOLEAN,
	"x_Spare3Running"	BOOLEAN,
	"x_Spare3Estop"	BOOLEAN
)
{{ mqtt_with('sail-systems/remotes') }}
