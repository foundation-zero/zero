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
	"xPull"	BOOLEAN,
	"xEase"	BOOLEAN,
	"xRunningCW"	BOOLEAN,
	"xRunningCCW"	BOOLEAN,
	"xSpeedDeviationAlarm"	BOOLEAN,
	"xDriveNotRunningAlarm"	BOOLEAN,
	"wActiveFault"	INTEGER,
	"rPullTorqueSetting"	REAL,
	"rEaseTorqueSetting"	REAL
)
{{ mqtt_with('sail-systems/fe206_mainsheetfeeder,sail-systems/fe505_mizzensheetfeeder') }}
