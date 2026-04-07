{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"DOOR_POWERSUPPLYFAIL"	{{ marpower_struct("BOOLEAN") }},
	"AUXILIARY_SYSTEM_SERVICESUPPLYFAIL"	{{ marpower_struct("BOOLEAN") }},
	"AUXILIARY_SYSTEM_EMERGENCYSUPPLYFAIL"	{{ marpower_struct("BOOLEAN") }},
	"DETECT_FAULT"	{{ marpower_struct("BOOLEAN") }},
	"DOORS_RELEASE"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-firedetection-general') }}
