{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"StatusOnOff"	{{ marpower_struct("BOOLEAN") }},
	"ExternalOff"	{{ marpower_struct("BOOLEAN") }},
	"Iwarning"	{{ marpower_struct("BOOLEAN") }},
	"UnderVoltage"	{{ marpower_struct("BOOLEAN") }},
	"ShortCircuit"	{{ marpower_struct("BOOLEAN") }},
	"SystemError"	{{ marpower_struct("BOOLEAN") }},
	"StatusHMIRed"	{{ marpower_struct("BOOLEAN") }},
	"StatusHMIGreen"	{{ marpower_struct("BOOLEAN") }},
	"StatusHMIYellow"	{{ marpower_struct("BOOLEAN") }},
	"OutputCurrent"	{{ marpower_struct("INTEGER") }},
	"Isetting"	{{ marpower_struct("INTEGER") }},
	"Csetting"	{{ marpower_struct("INTEGER") }},
	"HmiCmdOpen"	{{ marpower_struct("BOOLEAN") }},
	"HmiCmdClose"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-24vdc-system/#') }}
