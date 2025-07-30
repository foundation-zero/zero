{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	TIMESTAMP	TIMESTAMP,
	NOVEC_RELEASED_ALARM	BOOLEAN,
)
{{ mqtt_with('marpower/220000_novec') }}
