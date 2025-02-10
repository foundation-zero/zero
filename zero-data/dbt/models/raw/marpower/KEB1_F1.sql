{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	AmcsPlcPowerModule1InternalFuseBlown	BOOLEAN,
	AmcsPlcPowerModule1PowerFailure	BOOLEAN,
)
{{ mqtt_with('KEB1_F1') }}