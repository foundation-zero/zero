{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	AlarmPanelSilenceButton	BOOLEAN,
	Spare_DI01_2	BOOLEAN,
	AlarmPanelGeaCallRevokeButton	BOOLEAN,
	AlarmPanelAcknowledgeButton	BOOLEAN,
	Spare_DI01_5	BOOLEAN,
	Spare_DI01_6	BOOLEAN,
	Spare_DI01_7	BOOLEAN,
	Spare_DI01_8	BOOLEAN,
)
{{ mqtt_with('KEB1_DI01') }}