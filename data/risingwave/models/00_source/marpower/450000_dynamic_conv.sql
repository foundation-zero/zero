{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ACGRID_BUSTIEOPENED"	{{ marpower_struct("BOOLEAN") }},
	"ACGRID_BUSTIECLOSED"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-dynamic-conv') }}
