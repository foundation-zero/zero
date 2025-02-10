{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	ACC_SENSOR_1_OUTPY	REAL,
	ACC_SENSOR_1_OUTPZ	REAL,
	LEVEL_GREY_WATER_TANK_FWD_SB	REAL,
	TECH_WAT_FLOW_REEL_FOR_DECKWASH_B05	REAL,
)
{{ mqtt_with('KEB2_AI28') }}