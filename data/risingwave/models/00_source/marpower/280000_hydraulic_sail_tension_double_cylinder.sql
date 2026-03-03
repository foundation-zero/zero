{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_Stat_HMI"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Load_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_HMI_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Act_Position_2_Mill"	{{ marpower_struct("INTEGER") }},
	"Act_Position_Mill"	{{ marpower_struct("INTEGER") }},
	"Act_Load"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/tension-double-cylinder/#') }}
