{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"AlarmPanelSilenceButton"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelGeaCallRevokeButton"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelAcknowledgeButton"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelSilenceLight"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelGeaCallRevokeLight"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelAcknowledgeLight"	{{ marpower_struct("BOOLEAN") }},
	"BridgeAlarmPanelSilenceButton"	{{ marpower_struct("BOOLEAN") }},
	"OperatorAlarmPanelSilenceButton"	{{ marpower_struct("BOOLEAN") }},
	"BridgeAlarmPanelSilenceLight"	{{ marpower_struct("BOOLEAN") }},
	"OperatorAlarmPanelSilenceLight"	{{ marpower_struct("BOOLEAN") }},
	"OperatorAlarmPanelBuzzer"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-amcs/alarm_panel') }}
