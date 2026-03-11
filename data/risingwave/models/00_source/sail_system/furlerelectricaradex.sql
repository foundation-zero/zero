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
	"ox_Furl"	BOOLEAN,
	"ox_Unfurl"	BOOLEAN,
	"ix_RcFurl"	BOOLEAN,
	"ix_RcUnfurl"	BOOLEAN,
	"ix_LocalFurl"	BOOLEAN,
	"ix_LocalUnfurl"	BOOLEAN,
	"sDrive"	STRUCT<x_CanAlive BOOLEAN, x_Ready BOOLEAN, x_Running BOOLEAN, xFault BOOLEAN, iSpeedDemand INTEGER, iActualSpeed INTEGER, rTorqueDemand REAL, rActualTorque REAL, i_HeatsinkTemp INTEGER, rDcLinkVoltage REAL, duiRunningTime INTEGER, ow_Alarmcode INTEGER, WarningEncoder BOOLEAN, WarningHvInput BOOLEAN, WarningIgbt BOOLEAN, WarningMotorTemp BOOLEAN, WarningFcTemp BOOLEAN, WarningControl BOOLEAN, WarningCommunication BOOLEAN, WarningOthers BOOLEAN, ERROREncoder BOOLEAN, ERRORHvInput BOOLEAN, ERRORIgbt BOOLEAN, ERRORMotorTemp BOOLEAN, ERRORFcTemp BOOLEAN, ERRORControl BOOLEAN, ERRORCommunication BOOLEAN, ERROROthers BOOLEAN, wCanState INTEGER>,
	"i_FurlSpeedSetting"	INTEGER,
	"i_UnfurlSpeedSetting"	INTEGER
)
{{ mqtt_with('sail-systems/fe102_bladefurler') }}
