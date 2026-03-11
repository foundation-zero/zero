{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	time TIMESTAMPTZ AS proctime(),
	"ix_0000_BtnHydrStopTechRm"	BOOLEAN,
	"ix_0000_EStopRelay"	BOOLEAN,
	"ix_0000_HydrFireStop"	BOOLEAN,
	"ix_0000_BtnHydrStopHlmSb"	BOOLEAN,
	"ix_0000_BtnHydrStopMnMst"	BOOLEAN,
	"ix_0000_BtnHydrStopSlStrgLckr"	BOOLEAN,
	"ix_0000_BtnHydrEnblHlmPs"	BOOLEAN,
	"ix_0000_BtnHydrStopRcCckpt"	BOOLEAN,
	"ix_0000_BtnHydrStopHlyrdPt"	BOOLEAN,
	"ix_0000_BtnHydrStopHlmPs"	BOOLEAN,
	"ix_0000_BtnHydrStopMzznMst"	BOOLEAN
)
{{ mqtt_with('sail-systems/estop') }}
