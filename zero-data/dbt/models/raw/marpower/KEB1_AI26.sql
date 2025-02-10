{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	ACC_SENSOR_2_OUTPZ	REAL,
	PNEUMATIC_PRESSURE	REAL,
	LEVEL_GREY_WATER_TANK_AFT_SB	REAL,
	LEVEL_GREY_WATER_TANK_AFT_SB	REAL,
)
{{ mqtt_with('KEB1_AI26') }}