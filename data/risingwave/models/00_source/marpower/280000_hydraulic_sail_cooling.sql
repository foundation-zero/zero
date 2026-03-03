{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"fore_peak_no_flow_Alm"	{{ marpower_struct("BOOLEAN") }},
	"halyard_pit_no_flow_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Tech_space_no_flow_Alm"	{{ marpower_struct("BOOLEAN") }},
	"lazarette_no_flow_Alm"	{{ marpower_struct("BOOLEAN") }},
	"fore_peak_high_Cool_temp_Alm"	{{ marpower_struct("BOOLEAN") }},
	"halyard_pit_high_Cool_temp_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Tech_space_high_Cool_temp_Alm"	{{ marpower_struct("BOOLEAN") }},
	"lazarette_high_Cool_temp_Alm"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/cooling') }}
