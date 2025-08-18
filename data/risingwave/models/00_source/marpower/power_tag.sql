{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Active_Power_Phase_A"	{{ marpower_struct("REAL") }},
	"Active_Power_Phase_B"	{{ marpower_struct("REAL") }},
	"Active_Power_Phase_C"	{{ marpower_struct("REAL") }},
	"Power_Factor_Phase_A"	{{ marpower_struct("REAL") }},
	"Power_Factor_Phase_B"	{{ marpower_struct("REAL") }},
	"Power_Factor_Phase_C"	{{ marpower_struct("REAL") }},
	"RMS_Current_Phase_A"	{{ marpower_struct("REAL") }},
	"RMS_Current_Phase_B"	{{ marpower_struct("REAL") }},
	"RMS_Current_Phase_C"	{{ marpower_struct("REAL") }},
	"RMS_Current_Phase_Neut"	{{ marpower_struct("REAL") }},
	"RMS_Voltage_A_N"	{{ marpower_struct("REAL") }},
	"RMS_Voltage_B_N"	{{ marpower_struct("REAL") }},
	"RMS_Voltage_C_N"	{{ marpower_struct("REAL") }},
	"Total_Active_Power"	{{ marpower_struct("REAL") }},
	"Total_Power_Factor"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/power-tag/#') }}
