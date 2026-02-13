{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ow_ActLoad_10kg"	INTEGER,
	"relative_position_dummy"	INTEGER
)
{{ mqtt_with('sail-systems/f0402_mzznhdsladjstr') }}
