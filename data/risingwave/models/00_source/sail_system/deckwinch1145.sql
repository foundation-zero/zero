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
	"ix_Btn1"	BOOLEAN,
	"ix_Btn2"	BOOLEAN,
	"ix_Btn3"	BOOLEAN,
	"ix_SnsrSpd"	BOOLEAN,
	"ox_LoadAlarm"	BOOLEAN,
	"io_SpdStp1"	INTEGER,
	"io_SpdStp2"	INTEGER,
	"io_SpdStp3"	INTEGER,
	"io_SpdStp1Bw"	INTEGER
)
{{ mqtt_with('sail-systems/fe212_primarydeckwinchps,sail-systems/fe308_primarydeckwinchsb') }}
