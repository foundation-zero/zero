{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	AmcsPlcPowerModule1InternalFuseBlown	BOOLEAN,
	AmcsPlcPowerModule1PowerFailure	BOOLEAN,
	AmcsPlcPowerModule2FuseBlown	BOOLEAN,
	AmcsPlcPowerModule2PowerFailure	BOOLEAN,
)
{{ mqtt_with('KEB2_F2') }}