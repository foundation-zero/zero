{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	PASS_HATCH_CL_LOCK	BOOLEAN,
)
{{ mqtt_with('marpower/7500_passerelle') }}
