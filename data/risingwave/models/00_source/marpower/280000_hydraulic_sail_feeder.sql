{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Load_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Alm_Code"	{{ marpower_struct("INTEGER") }},
	"Act_Load"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/feeder/#') }}
