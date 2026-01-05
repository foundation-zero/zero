{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"WASH_1_LAUNDHEATDEM"	{{ marpower_struct("BOOLEAN") }},
	"WASH_2_LAUNDHEATDEM"	{{ marpower_struct("BOOLEAN") }},
	"DRYER_1_LAUNDHEATDEM"	{{ marpower_struct("BOOLEAN") }},
	"DRYER_2_LAUNDHEATDEM"	{{ marpower_struct("BOOLEAN") }},
	"DISH_WASH_CREWMESS_DEM"	{{ marpower_struct("BOOLEAN") }},
	"DISH_WASH1_GALLEY_DEM"	{{ marpower_struct("BOOLEAN") }},
	"DISH_WASH2_GALLEY_DEM"	{{ marpower_struct("BOOLEAN") }},
	"DISH_WASH_MAINSALONBAR_DEM"	{{ marpower_struct("BOOLEAN") }},
	"WASH_1_LAUND_HEATPER"	{{ marpower_struct("BOOLEAN") }},
	"WASH_2_LAUND_HEATPER"	{{ marpower_struct("BOOLEAN") }},
	"DRYER_1_LAUND_HEATPER"	{{ marpower_struct("BOOLEAN") }},
	"DRYER_2_LAUND_HEATPER"	{{ marpower_struct("BOOLEAN") }},
	"DISH_WASH_CREWMESSPER"	{{ marpower_struct("BOOLEAN") }},
	"DISH_WASH_1_GALLEYPER"	{{ marpower_struct("BOOLEAN") }},
	"DISH_WASH_2_GALLEYPER"	{{ marpower_struct("BOOLEAN") }},
	"DISH_WASH_MAINSALONBARPER"	{{ marpower_struct("BOOLEAN") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/270000-domestic-equipm') }}
