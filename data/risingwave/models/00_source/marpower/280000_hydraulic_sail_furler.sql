{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_Stat_HMI_Miz_headsail"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Miz_headsail"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Code"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Code"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Blade"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Blade"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Staysail"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Staysail"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Miz_headsail"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Code"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Blade"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Staysail"	{{ marpower_struct("BOOLEAN") }},
	"Storm_Sail_Act_Load"	{{ marpower_struct("INTEGER") }},
	"Code_Alm_Code"	{{ marpower_struct("INTEGER") }},
	"Blade_Alm_Code"	{{ marpower_struct("INTEGER") }},
	"Staysail_Alm_Code"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/furler') }}
