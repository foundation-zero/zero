{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_Stat_HMI_Oil_Supp_guest_Board_Syst_SB"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Oil_Supp_guest_Board_Syst_SB"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_Oil_Supp_Pass"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_Oil_Supp_Pass"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Oil_Supp_guest_Board_Syst_SB"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_Oil_Supp_Pass"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/boarding-equipment') }}
