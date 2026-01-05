{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"SPARE_DI"	{{ marpower_struct("BOOLEAN") }},
	"SPARE_DI36_6"	{{ marpower_struct("BOOLEAN") }},
	"SPARE_DI36_7"	{{ marpower_struct("BOOLEAN") }},
	"SPARE_DI36_8"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/hpu') }}
