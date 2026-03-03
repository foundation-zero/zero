{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_Stat_HMI"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Locked_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Unlocked_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Up_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Lock"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Lock"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Button_Open_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Button_Close_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Lock"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Act_position_Ext"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/crew-boarding-platform') }}
