{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ix_SnsrA2Lck"	BOOLEAN,
	"ix_SnsrA2LckOvrhst"	BOOLEAN,
	"ix_SnsrA3C0Lck"	BOOLEAN,
	"ix_SnsrA3C0LckOvrhst"	BOOLEAN,
	"ix_SnsrStyslLck"	BOOLEAN,
	"ix_SnsrStyslLckOvrhst"	BOOLEAN,
	"ix_SnsrSrmJpLck"	BOOLEAN,
	"ix_SnsrSrmJpLckOvrhst"	BOOLEAN
)
{{ mqtt_with('sail-systems/mast') }}
