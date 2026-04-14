{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"CB_10_COMALARM"	{{ marpower_struct("BOOLEAN") }},
	"CB_10_24VDCSERVFAIL"	{{ marpower_struct("BOOLEAN") }},
	"CB_10_24VDCEMERGFAIL"	{{ marpower_struct("BOOLEAN") }},
	"CB_11_COMALARM"	{{ marpower_struct("BOOLEAN") }},
	"CB_11_24VDCSERVFAIL"	{{ marpower_struct("BOOLEAN") }},
	"CB_11_24VDCEMERGFAIL"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/150000-pcs') }}
