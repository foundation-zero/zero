{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"PresetSelection"	{{ marpower_struct("INTEGER") }},
	"SliderRed"	{{ marpower_struct("INTEGER") }},
	"SliderGreen"	{{ marpower_struct("INTEGER") }},
	"SliderBlue"	{{ marpower_struct("INTEGER") }},
	"SliderWhite"	{{ marpower_struct("INTEGER") }},
	"PresetReset"	{{ marpower_struct("BOOLEAN") }},
	"PresetSet"	{{ marpower_struct("BOOLEAN") }},
	"SliderOnOff"	{{ marpower_struct("BOOLEAN") }},
	"ActiveChanges"	{{ marpower_struct("BOOLEAN") }},
	"Preset1HmiColor"	{{ marpower_struct("STRING") }},
	"Preset2HmiColor"	{{ marpower_struct("STRING") }},
	"Preset3HmiColor"	{{ marpower_struct("STRING") }},
	"Preset4HmiColor"	{{ marpower_struct("STRING") }},
	"Preset5HmiColor"	{{ marpower_struct("STRING") }},
	"Preset6HmiColor"	{{ marpower_struct("STRING") }},
	"CurrentHmiColor"	{{ marpower_struct("STRING") }},
)
INCLUDE partition AS topic
{{ mqtt_with('marpower/450000-underwlights/#') }}
