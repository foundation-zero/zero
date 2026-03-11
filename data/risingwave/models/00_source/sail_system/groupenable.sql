{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"st_AnchorWinches"	STRUCT<x_Enabled BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN>,
	"st_BoardingEquipment"	STRUCT<x_Enabled BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN>,
	"st_DeckWinches"	STRUCT<x_Enabled BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN>,
	"st_SailFunction"	STRUCT<x_Enabled BOOLEAN, x_OnOff BOOLEAN, x_ExtOnOff BOOLEAN>
)
{{ mqtt_with('sail-systems/groupreleases') }}
