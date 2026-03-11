{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"FE207_MnHlyrd"	STRUCT<ix_SnsrHlyrdLckFh BOOLEAN, ix_SnsrHlyrdLck1 BOOLEAN, ix_SnsrHlyrdLck2 BOOLEAN, ix_SnsrHlyrdLck3 BOOLEAN, ix_SnsrHlyrdLckFhOvrhst BOOLEAN, ix_SnsrHlyrdLck1Ovrhst BOOLEAN, ix_SnsrHlyrdLck2Ovrhst BOOLEAN, ix_SnsrHlyrdLck3Ovrhst BOOLEAN, ix_SnsrBmRfLck1 BOOLEAN, ix_SnsrBmRfLck2 BOOLEAN, ix_SnsrBmRfLck3 BOOLEAN>,
	"FE404_MzznHlyrd"	STRUCT<ix_SnsrHlyrdLckFh BOOLEAN, ix_SnsrHlyrdLck1 BOOLEAN, ix_SnsrHlyrdLck2 BOOLEAN, ix_SnsrHlyrdLckFhOvrhst BOOLEAN, ix_SnsrHlyrdLck1Ovrhst BOOLEAN, ix_SnsrHlyrdLck2Ovrhst BOOLEAN, ix_SnsrBmRfLck1 BOOLEAN, ix_SnsrBmRfLck2 BOOLEAN>,
	"F0401_MzznHdFrlr"	STRUCT<ix_SnsrHdslLck BOOLEAN, ix_SnsrHdslLckOvrhst BOOLEAN>,
	"ix_SnsrA2Lck"	BOOLEAN,
	"ix_SnsrA2LckOvrhst"	BOOLEAN,
	"ix_SnsrA3C0Lck"	BOOLEAN,
	"ix_SnsrA3C0LckOvrhst"	BOOLEAN,
	"ix_SnsrStyslLck"	BOOLEAN,
	"ix_SnsrStyslLckOvrhst"	BOOLEAN,
	"ix_SnsrSrmJpLck"	BOOLEAN,
	"ix_SnsrSrmJpLckOvrhst"	BOOLEAN,
	"StormSailFurlerLoad"	STRUCT<i_Load INTEGER, i_MaxLoadSetting INTEGER, x_MaxLimitReached BOOLEAN, x_Failure BOOLEAN>
)
{{ mqtt_with('sail-systems/mast') }}
