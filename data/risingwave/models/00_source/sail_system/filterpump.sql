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
	"x_SetModeOff"	BOOLEAN,
	"x_SetModeOn"	BOOLEAN,
	"x_SetModeAuto"	BOOLEAN,
	"x_ExtSetModeOff"	BOOLEAN,
	"x_ExtSetModeOn"	BOOLEAN,
	"x_ExtSetModeAuto"	BOOLEAN,
	"x_ModeOff"	BOOLEAN,
	"x_ModeOn"	BOOLEAN,
	"x_ModeAuto"	BOOLEAN,
	"ix_RelayStatus"	BOOLEAN,
	"i_OffDelayTime"	INTEGER,
	"st_powerEnable"	STRUCT<x_Maintenance BOOLEAN, x_FunctionEnabled BOOLEAN, x_GroupEnabled BOOLEAN, x_LocalControl BOOLEAN, x_RcControl BOOLEAN, x_Running BOOLEAN, ox_GnrlAlrm BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN, i_State INTEGER, ui_RunningHours INTEGER, ix_RelayStatus BOOLEAN, ox_PwrEnable BOOLEAN, x_PowerFailure BOOLEAN>
)
{{ mqtt_with('sail-systems/f001_filterpump') }}
