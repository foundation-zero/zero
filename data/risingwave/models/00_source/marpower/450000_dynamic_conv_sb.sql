{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"CURRENT"	{{ marpower_struct("REAL") }},
	"OVERCURRENT"	{{ marpower_struct("BOOLEAN") }},
	"VOLTAGE"	{{ marpower_struct("REAL") }},
	"UNDERVOLTAGE"	{{ marpower_struct("BOOLEAN") }},
	"OVERVOLTAGE"	{{ marpower_struct("BOOLEAN") }},
	"ACTIVEPOWER"	{{ marpower_struct("REAL") }},
	"REACTIVEPOWER"	{{ marpower_struct("REAL") }},
	"APPARENTPOWER"	{{ marpower_struct("REAL") }},
	"COSPHI"	{{ marpower_struct("REAL") }},
	"POWERFACTOR"	{{ marpower_struct("REAL") }},
	"FREQUENCY"	{{ marpower_struct("REAL") }},
	"NOZERO"	{{ marpower_struct("BOOLEAN") }},
	"VOLTAGESAG"	{{ marpower_struct("BOOLEAN") }},
	"4QUADRANT"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-dynamic-conv-sb/#') }}
