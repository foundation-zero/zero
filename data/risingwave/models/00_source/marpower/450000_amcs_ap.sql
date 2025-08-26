{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"AlarmPanelAcknowledgeButton"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelAcknowledgeLight"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelGeaCallRevokeButton"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelGeaCallRevokeLight"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelSilenceButton"	{{ marpower_struct("BOOLEAN") }},
	"AlarmPanelSilenceLight"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-amcs/ap') }}
