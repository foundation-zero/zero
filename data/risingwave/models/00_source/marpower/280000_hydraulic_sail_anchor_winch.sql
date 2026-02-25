{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_Stat_HMI_PS"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_PS"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_Stat_HMI_SB"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_SB"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_PS"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext_SB"	{{ marpower_struct("BOOLEAN") }},
	"PS_Alm_Code"	{{ marpower_struct("INTEGER") }},
	"PS_Chain_counter_Chain_length_Ext"	{{ marpower_struct("INTEGER") }},
	"SB_Alm_Code"	{{ marpower_struct("INTEGER") }},
	"SB_Chain_counter_Chain_length_Ext"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/anchor-winch') }}
