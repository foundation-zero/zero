{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	UmsMannedLight	BOOLEAN,
	UmsTimingOnLight	BOOLEAN,
	Spare_DO00_3	BOOLEAN,
	UmsOneManTimerResetLight	BOOLEAN,
	AlarmPanelSilenceLight	BOOLEAN,
	AlarmPanelGeaCallRevokeLight	BOOLEAN,
	MachinerySpaceBuzzerHorn	BOOLEAN,
	AlarmPanelAcknowledgeLight	BOOLEAN,
)
{{ mqtt_with('KEB1_DO00') }}