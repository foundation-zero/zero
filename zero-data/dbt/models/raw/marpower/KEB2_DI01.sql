{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	UmsCabin1Silence	BOOLEAN,
	UmsCabin2Silence	BOOLEAN,
	UmsCabin3Silence	BOOLEAN,
	Spare_DI01_4	BOOLEAN,
	Spare_DI01_5	BOOLEAN,
	Spare_DI01_6	BOOLEAN,
	Spare_DI01_7	BOOLEAN,
	Spare_DI01_8	BOOLEAN,
)
{{ mqtt_with('KEB2_DI01') }}