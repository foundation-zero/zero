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
	"x_In"	BOOLEAN,
	"x_Out"	BOOLEAN,
	"x_CylA"	BOOLEAN,
	"x_CylB"	BOOLEAN,
	"x_SensrIn"	BOOLEAN,
	"x_SensrOut"	BOOLEAN,
	"i_FeedForwardPressureSetting"	INTEGER,
	"ox_LoadAlarm"	BOOLEAN,
	"i_Load"	INTEGER,
	"st_load"	STRUCT<i_Load INTEGER, r_RawSensor REAL, i_MaxLoadSetting INTEGER, i_LoadChangePermA INTEGER, i_LoadAt4rmA INTEGER, x_MaxLimitReached BOOLEAN, x_Failure BOOLEAN>,
	"st_loadPs"	STRUCT<i_Load INTEGER, i_MaxLoadSetting INTEGER, x_MaxLimitReached BOOLEAN, x_Failure BOOLEAN>,
	"st_loadSb"	STRUCT<i_Load INTEGER, i_MaxLoadSetting INTEGER, x_MaxLimitReached BOOLEAN, x_Failure BOOLEAN>,
	"st_position"	STRUCT<i_Position_mm INTEGER, i_CylinderLength INTEGER, i_Speed INTEGER, x_MinLimitReached BOOLEAN, x_MaxLimitReached BOOLEAN, x_Failure BOOLEAN, i_Position_permille INTEGER, i_MinPosition INTEGER, i_MaxPosition INTEGER>
)
{{ mqtt_with('sail-systems/f0203_maincheckstaydeflector,sail-systems/f0503_mizzencheckstaydeflector') }}
