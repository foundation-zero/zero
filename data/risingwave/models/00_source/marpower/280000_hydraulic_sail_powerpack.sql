{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Ind_Run_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Manual_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_On_Off_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Auto_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Manual_Ext"	{{ marpower_struct("BOOLEAN") }},
	"On_Off_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Auto_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Run_hours"	{{ marpower_struct("INTEGER") }},
	"Igbt_Temperatuur"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_Ext"	{{ marpower_struct("INTEGER") }},
	"Flow_sensor_Ext"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/powerpack/#') }}
