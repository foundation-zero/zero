{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Setpoint"	{{ marpower_struct("INTEGER") }},
	"RelPos"	{{ marpower_struct("INTEGER") }},
	"AbsPos"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/000000-heatrecovery/vlv/#') }}
