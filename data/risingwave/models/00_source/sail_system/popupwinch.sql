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
	"sDrive"	STRUCT<x_CanAlive BOOLEAN, xReady BOOLEAN, xRun BOOLEAN, xRunning BOOLEAN, xBrake BOOLEAN, xFault BOOLEAN, ow_Alarmcode INTEGER, wCanState INTEGER, iSpeedDemand INTEGER, iActualSpeed INTEGER, rTorqueDemand REAL, rActualTorque REAL, rHeatsinkTemp REAL, rDcLinkVoltage REAL, duiRunningTime INTEGER>,
	"ix_BtnPull"	BOOLEAN,
	"ix_BtnEase"	BOOLEAN,
	"ix_LmtdSpdSnsr"	BOOLEAN,
	"i_PullSpeedSetting"	INTEGER,
	"i_EaseSpeedSetting"	INTEGER
)
{{ mqtt_with('sail-systems/fe406_popupcapstanps,sail-systems/fe506_popupcapstansb') }}
