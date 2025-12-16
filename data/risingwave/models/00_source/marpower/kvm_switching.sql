{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"HELM_PS_OUT_DISP_ONOFF"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_OUT_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_IN_DISP_ONOFF"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_IN_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_IN_DISP_AMCS"	{{ marpower_struct("BOOLEAN") }},
	"SHIPS_OFF_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"HELM_PS_IN_MOUSE_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"CAPT_CAB_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"MISSION_RM_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"CREW_MESS_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"HELM_SB_OUT_DISP_ONOFF"	{{ marpower_struct("BOOLEAN") }},
	"HELM_SB_OUT_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"HELM_SB_IN_DISP_ONOFF"	{{ marpower_struct("BOOLEAN") }},
	"HELM_SB_IN_DISP_TOGG"	{{ marpower_struct("BOOLEAN") }},
	"Spare_DI33_1"	{{ marpower_struct("BOOLEAN") }},
	"Spare_DI33_2"	{{ marpower_struct("BOOLEAN") }},
	"Spare_DI33_3"	{{ marpower_struct("BOOLEAN") }},
	"HELM_SB_IN_MOUSE_TOGG"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/kvm-switching') }}
