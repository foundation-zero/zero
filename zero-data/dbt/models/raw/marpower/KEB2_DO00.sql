{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	UmsCabin1Buzzer	BOOLEAN,
	UmsCabin2Buzzer	BOOLEAN,
	UmsCabin3Buzzer	BOOLEAN,
	BridgeAlarmPanelSilenceLight	BOOLEAN,
	OperatorAlarmPanelSilenceLight	BOOLEAN,
	MachinerySpaceBuzzerHorn	BOOLEAN,
	BridgeAlarmPanelBuzzer	BOOLEAN,
	OperatorAlarmPanelBuzzer	BOOLEAN,
)
{{ mqtt_with('KEB2_DO00') }}