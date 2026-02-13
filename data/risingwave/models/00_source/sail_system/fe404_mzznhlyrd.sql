{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ow_ActLoad_10kg"	INTEGER,
	"ox_IndctMzznHlyrdLckFh_Ext"	BOOLEAN,
	"ox_IndctMzznHlyrdLck1_Ext"	BOOLEAN,
	"ox_IndctMzznHlyrdLck2_Ext"	BOOLEAN,
	"ox_IndctMzznHlyrdLckFhOvrhst_Ext"	BOOLEAN,
	"ox_IndctMzznHlyrdLck1Ovrhst_Ext"	BOOLEAN,
	"ox_IndctMzznHlyrdLck2Ovrhst_Ext"	BOOLEAN,
	"ox_IndctMzznBmRfLck1_Ext"	BOOLEAN,
	"ox_IndctMzznBmRfLck2_Ext"	BOOLEAN
)
{{ mqtt_with('sail-systems/fe404_mzznhlyrd') }}
