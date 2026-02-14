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
	"i_MaxTorqueStp"	INTEGER,
	"i_MaxSpeedStp"	INTEGER
)
{{ mqtt_with('sail-systems/fe202_bladesheetpsfeeder,sail-systems/fe204_staysailsheetpsfeeder,sail-systems/fe302_bladesheetsbfeeder,sail-systems/fe304_staysailsheetsbfeeder') }}
