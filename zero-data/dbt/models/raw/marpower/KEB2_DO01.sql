{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	UMSCabin1Duty	BOOLEAN,
	UMSCabin1AlarmLed	BOOLEAN,
	UMSCabin2Duty	BOOLEAN,
	UMSCabin2AlarmLed	BOOLEAN,
	UMSCabin3Duty	BOOLEAN,
	UMSCabin3AlarmLed	BOOLEAN,
	Spare_DO01_7	BOOLEAN,
	Spare_DO01_8	BOOLEAN,
)
{{ mqtt_with('KEB2_DO01') }}