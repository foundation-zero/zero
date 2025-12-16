{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"UGRID_AFT_ENABLE"	{{ marpower_struct("BOOLEAN") }},
	"UGRID_AFT_ENABLEFIRMWARE"	{{ marpower_struct("BOOLEAN") }},
	"UGRID_AFT_DIGOUT1"	{{ marpower_struct("BOOLEAN") }},
	"UGRID_AFT_DIGOUT2"	{{ marpower_struct("BOOLEAN") }},
	"UGRID_FWD_ENABLE"	{{ marpower_struct("BOOLEAN") }},
	"UGRID_FWD_ENABLEFIRMWARE"	{{ marpower_struct("BOOLEAN") }},
	"UGRID_FWD_DIGOUT1"	{{ marpower_struct("BOOLEAN") }},
	"UGRID_FWD_DIGOUT2"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-ugrid') }}
