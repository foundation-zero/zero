{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Flow"	{{ marpower_struct("REAL") }},
	"Quantity"	{{ marpower_struct("REAL") }},
	"Temperature"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/500000-thrs/boilers/#') }}
