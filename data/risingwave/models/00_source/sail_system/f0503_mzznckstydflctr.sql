{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"relative_position_dummy"	INTEGER,
	"ow_ActLoad_10kg"	INTEGER,
	"ow_RelfLoad_10kg"	INTEGER,
	"ox_LoadAlarm"	BOOLEAN,
	"i_ActualLoadPs"	INTEGER,
	"i_ActualLoadSb"	INTEGER
)
{{ mqtt_with('sail-systems/f0503_mzznckstydflctr') }}
