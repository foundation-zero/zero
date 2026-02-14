{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"x_Maintenance"	BOOLEAN,
	"x_FunctionEnabled"	BOOLEAN,
	"x_GroupEnabled"	BOOLEAN,
	"x_LocalControl"	BOOLEAN,
	"x_RcControl"	BOOLEAN,
	"x_Running"	BOOLEAN,
	"ox_GnrlAlrm"	BOOLEAN,
	"x_OnOff"	BOOLEAN,
	"x_ExtOnOff"	BOOLEAN,
	"i_State"	INTEGER,
	"ui_RunningHours"	INTEGER,
	"ix_RelayStatus"	BOOLEAN,
	"ox_PwrEnable"	BOOLEAN,
	"x_PowerFailure"	BOOLEAN,
	"ix_OilRqst"	BOOLEAN,
	"ix_Estop"	BOOLEAN,
	"ox_SystmEnbl"	BOOLEAN,
	"ox_HpuRnnng"	BOOLEAN,
	"ox_Sailsystm"	BOOLEAN,
	"ox_PwrEnablePP"	BOOLEAN,
	"i_FeedForwardPressure"	INTEGER,
	"x_UseSailSystem"	BOOLEAN,
	"x_UsePowerPack"	BOOLEAN,
	"rFlowDemand"	INTEGER
)
{{ mqtt_with('sail-systems/f0600_tendercrane') }}
