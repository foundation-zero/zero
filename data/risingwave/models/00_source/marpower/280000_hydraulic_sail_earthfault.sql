{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"Isolated_DC_FPK_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Isolated_DC_MAIN_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Isolated_DC_HYP_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Isolated_DC_LAZ_Alm"	{{ marpower_struct("BOOLEAN") }},
	"Isolated_DC_FPK_Measure"	{{ marpower_struct("INTEGER") }},
	"Isolated_DC_MAIN_Measure"	{{ marpower_struct("INTEGER") }},
	"Isolated_DC_HYP_Measure"	{{ marpower_struct("INTEGER") }},
	"Isolated_DC_LAZ_Measure"	{{ marpower_struct("INTEGER") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/280000-hydraulic-sail/earthfault') }}
