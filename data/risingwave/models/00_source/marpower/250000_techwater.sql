{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"DRAIN_VLV_Y01_POS_OVERBOARD"	{{ marpower_struct("BOOLEAN") }},
	"CHLORINE_UNIT_ALARM"	{{ marpower_struct("BOOLEAN") }},
	"MTS_INLET_FIRE_FLAP_RELEASED"	{{ marpower_struct("BOOLEAN") }},
	"MTS_INLET_FIRE_FLAP_FULLY_RESET"	{{ marpower_struct("BOOLEAN") }},
	"MTS_EXHAUST_FIRE_FLAP_RELEASED"	{{ marpower_struct("BOOLEAN") }},
	"MTS_EXHAUST_FIRE_FLAP_FULLY_RESET"	{{ marpower_struct("BOOLEAN") }},
	"SALINITY1"	{{ marpower_struct("REAL") }},
	"TANK1_LEVEL"	{{ marpower_struct("REAL") }},
	"TANK2_LEVEL"	{{ marpower_struct("REAL") }},
	"CHARCOAL_FILTER_B01_FLOW"	{{ marpower_struct("REAL") }},
	"CHARCOAL_FILTER_B01_TEMP"	{{ marpower_struct("REAL") }},
	"ADIABATIC_COOL_B03_FLOW"	{{ marpower_struct("REAL") }},
	"ADIABATIC_COOL_B09_FLOW"	{{ marpower_struct("REAL") }},
	"REEL_FOR_DECKWASH_B05_FLOW"	{{ marpower_struct("REAL") }},
	"REEL_FOR_DECKWASH_B06_FLOW"	{{ marpower_struct("REAL") }},
	"VALVE_COLD_AIR_FR68_Y03_OPENCLOSE"	{{ marpower_struct("BOOLEAN") }},
	"VALVE_COLD_AIR_FR32_Y04_OPENCLOSE"	{{ marpower_struct("BOOLEAN") }},
	"VALVE_COLD_AIR_FR32_Y05_OPENCLOSE"	{{ marpower_struct("BOOLEAN") }},
	"DRAIN_VLV_Y02_POS_OVERBOARD"	{{ marpower_struct("BOOLEAN") }},
	"REEL_FOR_DECKWASH_B04_FLOW"	{{ marpower_struct("REAL") }},
	"SALINITY2"	{{ marpower_struct("REAL") }},
	"ADIABATIC_COOL_B07_FLOW"	{{ marpower_struct("REAL") }},
	"ADIABATIC_COOL_B08_FLOW"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/250000-techwater') }}
