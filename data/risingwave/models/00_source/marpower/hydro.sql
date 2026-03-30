{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Total_Active_Power"	{{ marpower_struct("REAL") }},
	"Total_Power_Factor"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/hydro/#') }}
