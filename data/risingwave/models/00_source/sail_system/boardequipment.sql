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
	"ix_OilRqst"	BOOLEAN,
	"ix_HtchClsdLckd"	BOOLEAN,
	"ox_SystmEnbl"	BOOLEAN,
	"ox_OilsplyB"	BOOLEAN,
	"i_FeedForwardPressureSetting"	INTEGER
)
{{ mqtt_with('sail-systems/f0405_oilsupplyguestboardingsystemsb,sail-systems/f0505_oilsupplypassarelle') }}
