{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Ind_fire_stop"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Helm_PS"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Helm_SB"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Tech_room"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Main_Mst"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Miz_Mst"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Sail_Stor_locker"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Halyard_pit"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Race_cockpit"	{{ marpower_struct("BOOLEAN") }},
	"Ind_Syst_Enbl_Ext"	{{ marpower_struct("BOOLEAN") }},
	"Button_Syst_Enbl_Ext"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/e-stop') }}
