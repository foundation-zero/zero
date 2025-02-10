{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	AmcsPowerSupplyFailure	BOOLEAN,
	Spare_DI00_2	BOOLEAN,
	Spare_DI00_3	BOOLEAN,
	Spare_DI00_4	BOOLEAN,
	BridgeBuzzersPowerSupplyFailure	BOOLEAN,
	BridgeAlarmPanelSilenceButton	BOOLEAN,
	OperatorBuzzersPowerSupplyFailure	BOOLEAN,
	OperatorAlarmPanelSilenceButton	BOOLEAN,
)
{{ mqtt_with('KEB2_DI00') }}