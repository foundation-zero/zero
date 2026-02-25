{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Ind_Offline_filter_unit_Run_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Offline_filter_Manual_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Offline_filter_On_Off_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Offline_filter_Auto_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Offline_filter_unit_Power_Supp_ok"	{{ marpower_struct("BOOLEAN") }},
	"Offline_filter_Manual_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Offline_filter_On_Off_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Offline_filter_Auto_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Offline_filter_Run_hours"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/filter-pump') }}
