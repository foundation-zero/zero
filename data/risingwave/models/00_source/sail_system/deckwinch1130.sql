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
	"ix_Btn1"	BOOLEAN,
	"ix_Btn2"	BOOLEAN,
	"ix_SnsrSpd"	BOOLEAN,
	"ox_LoadAlarm"	BOOLEAN,
	"io_SpdStp1"	INTEGER,
	"io_SpdStp2"	INTEGER,
	"io_SpdStp3"	INTEGER
)
{{ mqtt_with('sail-systems/fe104_bowdeckwinchps,sail-systems/fe105_bowdeckwinchsb,sail-systems/fe209_mainmastdeckwinchpsfwd,sail-systems/fe210_mainmastdeckwinchpsaft,sail-systems/fe305_mainmastdeckwinchsbfwd,sail-systems/fe306_mainmastdeckwinchsbaft,sail-systems/fe407_mizzenmastdeckwinchps,sail-systems/fe507_mizzenmastdeckwinchsb') }}
