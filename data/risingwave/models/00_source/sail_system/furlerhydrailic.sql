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
	"ix_BtnFrl"	BOOLEAN,
	"ix_BtnUnfrl"	BOOLEAN,
	"ix_RcFurl"	BOOLEAN,
	"ix_RcUnfurl"	BOOLEAN,
	"oi_FrlrA"	INTEGER,
	"oi_FrlrB"	INTEGER,
	"ii_FrlrA_Current"	INTEGER,
	"ii_FrlrB_Current"	INTEGER,
	"iFurlSpeedSetting"	INTEGER,
	"iUnfurlSpeedSetting"	INTEGER,
	"iFeedForwardPressure"	INTEGER
)
{{ mqtt_with('sail-systems/f0401_mizzenheadsailfurler') }}
