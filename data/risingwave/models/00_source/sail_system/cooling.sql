{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"sFrpk"	STRUCT<x_Maintenance BOOLEAN, x_FunctionEnabled BOOLEAN, x_GroupEnabled BOOLEAN, x_LocalControl BOOLEAN, x_RcControl BOOLEAN, x_Running BOOLEAN, ox_GnrlAlrm BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN, i_State INTEGER, ui_RunningHours INTEGER, x_NoFeedbackAlarm BOOLEAN, x_NoFlowAlarm BOOLEAN, x_TempAlarm BOOLEAN, i_Temperature INTEGER>,
	"sHlyrdpt"	STRUCT<x_Maintenance BOOLEAN, x_FunctionEnabled BOOLEAN, x_GroupEnabled BOOLEAN, x_LocalControl BOOLEAN, x_RcControl BOOLEAN, x_Running BOOLEAN, ox_GnrlAlrm BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN, i_State INTEGER, ui_RunningHours INTEGER, x_NoFeedbackAlarm BOOLEAN, x_NoFlowAlarm BOOLEAN, x_TempAlarm BOOLEAN, i_Temperature INTEGER>,
	"sTchSpc"	STRUCT<x_Maintenance BOOLEAN, x_FunctionEnabled BOOLEAN, x_GroupEnabled BOOLEAN, x_LocalControl BOOLEAN, x_RcControl BOOLEAN, x_Running BOOLEAN, ox_GnrlAlrm BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN, i_State INTEGER, ui_RunningHours INTEGER, x_NoFeedbackAlarm BOOLEAN, x_NoFlowAlarm BOOLEAN, x_TempAlarm BOOLEAN, i_Temperature INTEGER>,
	"sLzrtt"	STRUCT<x_Maintenance BOOLEAN, x_FunctionEnabled BOOLEAN, x_GroupEnabled BOOLEAN, x_LocalControl BOOLEAN, x_RcControl BOOLEAN, x_Running BOOLEAN, ox_GnrlAlrm BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN, i_State INTEGER, ui_RunningHours INTEGER, x_NoFeedbackAlarm BOOLEAN, x_NoFlowAlarm BOOLEAN, x_TempAlarm BOOLEAN, i_Temperature INTEGER>,
	"iDelayTime"	INTEGER
)
{{ mqtt_with('sail-systems/coolingpumps') }}
