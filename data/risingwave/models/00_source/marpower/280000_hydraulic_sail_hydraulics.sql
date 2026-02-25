{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Tank_Low_low_level_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Tank_Low_level_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Tank_Temperatur_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Tank_level_sensor"	{{ marpower_struct("INTEGER") }},
	"Tank_Temperatur_sensor_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_valve_block_1_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_valve_block_2_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_valve_block_3_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_valve_block_4_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_valve_block_5_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_valve_block_6_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_Aft_Syst_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_Fwd_Syst_Ext"	{{ marpower_struct("INTEGER") }},
	"Pressure_sensor_Retour_Ext"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/hydraulics') }}
