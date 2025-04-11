{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	NOVEC_BREAKER_TRIPPED_ALARM	BOOLEAN,
	NOVEC_RELEASED_ALARM	BOOLEAN,
)
{{ mqtt_with('marpower/2200_novec') }}
