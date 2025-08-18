{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"GAS_DETECTION_LVL_SWITCH"	{{ marpower_struct("BOOLEAN") }},
	"GAS_DETECTION_PERCT"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-gas-detection') }}
