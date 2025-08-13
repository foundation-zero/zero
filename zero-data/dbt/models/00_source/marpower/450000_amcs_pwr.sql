{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"AmcsPlcPowerModule1InternalFuseBlown"	{{ marpower_struct("BOOLEAN") }},
	"AmcsPlcPowerModule1PowerFailure"	{{ marpower_struct("BOOLEAN") }},
	"AmcsPlcPowerModule2FuseBlown"	{{ marpower_struct("BOOLEAN") }},
	"AmcsPlcPowerModule2PowerFailure"	{{ marpower_struct("BOOLEAN") }},
	"AmcsPowerSupplyFailure"	{{ marpower_struct("BOOLEAN") }},
	"FieldVoltageAvailable"	{{ marpower_struct("BOOLEAN") }},
	"GFDEnabled"	{{ marpower_struct("BOOLEAN") }},
	"MA0V"	{{ marpower_struct("BOOLEAN") }},
	"MA24V"	{{ marpower_struct("BOOLEAN") }},
	"PA0V"	{{ marpower_struct("BOOLEAN") }},
	"PA24V"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-amcs/pwr') }}
