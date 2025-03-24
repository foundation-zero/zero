{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	PASS_HATCH_CL_LOCK	BOOLEAN,
)
{{ mqtt_with('7500_passerelle') }}