{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TECH_WAT_FLOW_REEL_FOR_DECKWASH_B06	REAL,
)
{{ mqtt_with('KEB2_AI29') }}