{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"HELM_PS_IN_DISP_AMCS"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_IN_DISP_ON_OFF"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_IN_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_OUT_DISP_ON_OFF"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_OUT_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"SHIPS_OFF_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/kvm-switching/') }}
