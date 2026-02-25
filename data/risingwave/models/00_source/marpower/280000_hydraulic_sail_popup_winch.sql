{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_Stat_HMI"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Alm_Code"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/popup-winch/#') }}
