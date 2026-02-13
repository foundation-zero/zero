{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ox_IndctA2Lck_Ext"	BOOLEAN,
	"ox_IndctA2LckOvrhst_Ext"	BOOLEAN,
	"ox_IndctA3C0Lck_Ext"	BOOLEAN,
	"ox_IndctA3C0LckOverhst_Ext"	BOOLEAN,
	"ox_IndctStyslLck_Ext"	BOOLEAN,
	"ox_IndctStyslLckOverhst_Ext"	BOOLEAN,
	"ox_IndctStmjbLck_Ext"	BOOLEAN,
	"ox_IndctStmjbLckOvrhst_Ext"	BOOLEAN
)
{{ mqtt_with('sail-systems/mnmst') }}
