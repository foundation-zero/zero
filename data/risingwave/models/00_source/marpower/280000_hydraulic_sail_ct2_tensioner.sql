{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Main_Alm_Code"	{{ marpower_struct("INTEGER") }},
	"Miz_Alm_Code"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/ct2-tensioner') }}
