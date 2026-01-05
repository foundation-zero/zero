{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"cell1"	{{ marpower_struct("REAL") }},
	"cell2"	{{ marpower_struct("REAL") }},
	"cell3"	{{ marpower_struct("REAL") }},
	"cell4"	{{ marpower_struct("REAL") }},
	"cell5"	{{ marpower_struct("REAL") }},
	"cell6"	{{ marpower_struct("REAL") }},
	"cell7"	{{ marpower_struct("REAL") }},
	"cell8"	{{ marpower_struct("REAL") }},
	"cell9"	{{ marpower_struct("REAL") }},
	"cell10"	{{ marpower_struct("REAL") }},
	"cell11"	{{ marpower_struct("REAL") }},
	"cell12"	{{ marpower_struct("REAL") }},
	"cell13"	{{ marpower_struct("REAL") }},
	"cell14"	{{ marpower_struct("REAL") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-main-power-storage/#') }}
