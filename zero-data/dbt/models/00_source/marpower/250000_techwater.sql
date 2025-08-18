{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"DRAIN_VLV_Y01_POS_OVERBOARD"	{{ marpower_struct("BOOLEAN") }},
	"DRAIN_VLV_Y01_POS_TO_PURO"	{{ marpower_struct("BOOLEAN") }},
	"MTS_EXHAUST_FIRE_FLAP_FULLY_RESET"	{{ marpower_struct("BOOLEAN") }},
	"MTS_EXHAUST_FIRE_FLAP_RELEASED"	{{ marpower_struct("BOOLEAN") }},
	"MTS_INLET_FIRE_FLAP_FULLY_RESET"	{{ marpower_struct("BOOLEAN") }},
	"MTS_INLET_FIRE_FLAP_RELEASED"	{{ marpower_struct("BOOLEAN") }},
	"TECH_WATER_CHLORINE_UNIT_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"TECH_WAT_FLOW_ADIABATIC_COOL_B03"	{{ marpower_struct("REAL") }},
	"TECH_WAT_FLOW_ADIABATIC_COOL_B09"	{{ marpower_struct("REAL") }},
	"TECH_WAT_FLOW_CHARCOAL_FILTER_B01"	{{ marpower_struct("REAL") }},
	"TECH_WAT_FLOW_REEL_FOR_DECKWASH_B04"	{{ marpower_struct("REAL") }},
	"TECH_WAT_TANK1_LEVEL"	{{ marpower_struct("REAL") }},
	"TECH_WAT_TANK2_LEVEL"	{{ marpower_struct("REAL") }},
	"TECH_WAT_TEMP_CHARCOAL_FILTER_B01"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/250000-techwater/') }}
