{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ow_ActLoad_10kg"	INTEGER,
	"ox_IndctHlyrdLckFh_Ext"	BOOLEAN,
	"ox_IndctHlyrdLck1_Ext"	BOOLEAN,
	"ox_IndctHlyrdLck2_Ext"	BOOLEAN,
	"ox_IndctHlyrdLck3_Ext"	BOOLEAN,
	"ox_IndctHlyrdLckFhOvrhst_Ext"	BOOLEAN,
	"ox_IndctHlyrdLck1Ovrhst_Ext"	BOOLEAN,
	"ox_IndctHlyrdLck2Ovrhst_Ext"	BOOLEAN,
	"ox_IndctHlyrdLck3Ovrhst_Ext"	BOOLEAN,
	"ox_IndctBmRfLck1_Ext"	BOOLEAN,
	"ox_IndctBmRfLck2_Ext"	BOOLEAN,
	"ox_IndctBmRfLck3_Ext"	BOOLEAN
)
{{ mqtt_with('sail-systems/fe207_mnhlyrd') }}
