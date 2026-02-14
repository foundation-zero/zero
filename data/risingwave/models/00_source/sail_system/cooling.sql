{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"iDelayTime"	INTEGER
)
{{ mqtt_with('sail-systems/coolingpumps') }}
