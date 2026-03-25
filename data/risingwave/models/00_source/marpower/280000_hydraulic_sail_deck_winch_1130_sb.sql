{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_Stat_HMI_Bow"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Bow"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Main_Mst_Fwd"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Main_Mst_Fwd"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Main_Mst_Aft"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Main_Mst_Aft"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Miz_Mst"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Miz_Mst"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Bow"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Main_Mst_Fwd"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Main_Mst_Aft"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Miz_Mst"	{{ marpower_struct("BOOLEAN") }},
	"Bow_Alm_Code"	{{ marpower_struct("INTEGER") }},
	"Main_Mst_Fwd_Alm_Code"	{{ marpower_struct("INTEGER") }},
	"Main_Mst_Aft_Alm_Code"	{{ marpower_struct("INTEGER") }},
	"Miz_Mst_Alm_Code"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/deck-winch-1130/sb') }}
