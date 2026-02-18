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
	"ox_Pull"	BOOLEAN,
	"ox_Ease"	BOOLEAN,
	"xSpeedDeviationAlarm"	BOOLEAN,
	"ox_LoadAlarm"	BOOLEAN,
	"sDrive"	STRUCT<x_CanAlive BOOLEAN, xReady BOOLEAN, xRun BOOLEAN, xRunning BOOLEAN, xBrake BOOLEAN, xFault BOOLEAN, ow_Alarmcode INTEGER, wCanState INTEGER, iSpeedDemand INTEGER, iActualSpeed INTEGER, rTorqueDemand REAL, rActualTorque REAL, rHeatsinkTemp REAL, rDcLinkVoltage REAL, duiRunningTime INTEGER>,
	"st_load"	STRUCT<i_Load INTEGER, r_RawSensor REAL, i_MaxLoadSetting INTEGER, i_LoadChangePermA INTEGER, i_LoadAt4rmA INTEGER, x_MaxLimitReached BOOLEAN, x_Failure BOOLEAN>,
	"i_MaxTorqueStp"	INTEGER,
	"i_MaxSpeedStp"	INTEGER
)
{{ mqtt_with('sail-systems/fe202_bladesheetpsfeeder,sail-systems/fe204_staysailsheetpsfeeder,sail-systems/fe302_bladesheetsbfeeder,sail-systems/fe304_staysailsheetsbfeeder') }}
