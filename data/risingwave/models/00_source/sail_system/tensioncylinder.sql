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
	"ox_LoadAlarm"	BOOLEAN
)
{{ mqtt_with('sail-systems/f0201_mainouthaul,sail-systems/f0206_bladetweakerps,sail-systems/f0207_bladetweakersb,sail-systems/f0402_mizzenheadsailtackadjuster,sail-systems/f0501_mizzenouthaul') }}
