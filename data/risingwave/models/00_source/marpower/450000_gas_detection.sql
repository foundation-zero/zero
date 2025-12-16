{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"45008030_03"	{{ marpower_struct("REAL") }},
	"45008030_04"	{{ marpower_struct("REAL") }},
	"LVL_SWITCHACTIVE"	{{ marpower_struct("BOOLEAN") }},
	"PERCT"	{{ marpower_struct("REAL") }},
	"45008030_01"	{{ marpower_struct("REAL") }},
	"45008030_02"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-gas-detection') }}
