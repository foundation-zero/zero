{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Enbl_6_00_Stat_HMI_Tender_crane"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_6_00_Tender_crane"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_E1_08_Stat_HMI_Sail_drum"	{{ marpower_struct("BOOLEAN") }},
	"Gen_Alm_E1_08_Sail_drum"	{{ marpower_struct("BOOLEAN") }},
	"Fifi_pump_Run"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_6_00_HMI_Ext_Tender_crane"	{{ marpower_struct("BOOLEAN") }},
	"Enbl_E1_08_HMI_Ext_Sail_drum"	{{ marpower_struct("BOOLEAN") }},
	"Fifi_pump_start_request"	{{ marpower_struct("BOOLEAN") }},
	"Fifi_pump_stop_request"	{{ marpower_struct("BOOLEAN") }},
	"Miz_Check_Sb_Act_Load2"	{{ marpower_struct("INTEGER") }},
	"Main_boom_Prev_Act_Load2"	{{ marpower_struct("INTEGER") }},
	"Miz_boom_Prev_loadpin"	{{ marpower_struct("INTEGER") }},
	"Depth"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail') }}
