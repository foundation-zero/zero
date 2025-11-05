{{ config(materialized='table_with_connector') }}
CREATE TABLE {{ this }} (
	avg_daily_consumption_timestamp TIMESTAMPTZ AS proctime(),
	avg_daily_consumption float
)
