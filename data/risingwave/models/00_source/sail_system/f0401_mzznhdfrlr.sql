{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ox_IndctHdslLck_Ext"	BOOLEAN,
	"ox_IndctHdslLckOvrhst_Ext"	BOOLEAN
)
{{ mqtt_with('sail-systems/f0401_mzznhdfrlr') }}
