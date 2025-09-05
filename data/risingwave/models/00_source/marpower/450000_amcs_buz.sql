{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"MachinerySpaceBuzzerHorn"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-amcs/buz') }}
