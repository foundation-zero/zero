{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	AmcsPlcPowerModule2FuseBlown	BOOLEAN,
	AmcsPlcPowerModule2PowerFailure	BOOLEAN,
)
{{ mqtt_with('KEB1_F2') }}