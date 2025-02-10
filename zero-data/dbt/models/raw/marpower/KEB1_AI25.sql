{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TEMP1_FOR_ENERGY_REC_SYSTEM	REAL,
	TEMP2_FOR_ENERGY_REC_SYSTEM	REAL,
	ACC_SENSOR_2_OUTPX	REAL,
	ACC_SENSOR_2_OUTPY	REAL,
)
{{ mqtt_with('KEB1_AI25') }}