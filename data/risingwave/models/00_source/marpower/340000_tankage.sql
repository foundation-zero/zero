{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"HOTWATER11_LEVEL"	{{ marpower_struct("REAL") }},
	"HOTWATER13_LEVEL"	{{ marpower_struct("REAL") }},
	"HOTWATER15_LEVEL"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/340000-tankage') }}
