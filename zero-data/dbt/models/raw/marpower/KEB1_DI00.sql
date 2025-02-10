{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	AmcsPowerSupplyFailure	BOOLEAN,
	Spare_DI00_2	BOOLEAN,
	UmsEntranceUnitMannedSwitch	BOOLEAN,
	UmsEntranceUnitUnmannedSwitch	BOOLEAN,
	UmsEntranceUnitOneManSwitch	BOOLEAN,
	UmsEntranceUnitMoreMenSwitch	BOOLEAN,
	UmsOneManTimerResetButton	BOOLEAN,
	Spare_DI00_8	BOOLEAN,
)
{{ mqtt_with('KEB1_DI00') }}