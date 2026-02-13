{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ow_ActLoad_10kg"	INTEGER
)
{{ mqtt_with('sail-systems/fe408_aftwnchps') }}
