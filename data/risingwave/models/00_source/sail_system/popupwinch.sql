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
	"ix_BtnPull"	BOOLEAN,
	"ix_BtnEase"	BOOLEAN,
	"ix_LmtdSpdSnsr"	BOOLEAN,
	"i_PullSpeedSetting"	INTEGER,
	"i_EaseSpeedSetting"	INTEGER
)
{{ mqtt_with('sail-systems/fe406_popupcapstanps,sail-systems/fe506_popupcapstansb') }}
