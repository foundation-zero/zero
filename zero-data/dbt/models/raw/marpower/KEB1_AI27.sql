{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	LEVEL_SLUDGE_TANK	REAL,
	MAIN_DECKH_VENT_HATCH_SB_PERC	REAL,
	MAIN_DECKH_VENT_HATCH_PS_PERC	REAL,
	AFT_DECKH_VENT_HATCH_PERC	REAL,
)
{{ mqtt_with('KEB1_AI27') }}