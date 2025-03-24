{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	NOVEC_RELEASED_ALARM	BOOLEAN,
)
{{ mqtt_with('2200_novec') }}