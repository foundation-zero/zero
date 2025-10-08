{{ config(materialized='materialized_view') }}
{%- set tables = ['power_tag', 'pvt', 'shore_power', 'hydrogeneration'] -%}
SELECT 
	source_data.topic,
	source_data.time,
	(source_data.total_active_power)."Value" AS active_power,
	(source_data.total_active_power).TimeStamp AS active_power_timestamp,
	(source_data.total_active_power)."Value" AS power_factor,
	(source_data.total_active_power).TimeStamp AS power_factor_timestamp
FROM ( {{ get_marpower_power_data(tables) }} ) AS source_data
ASOF JOIN ( {{ get_marpower_power_data(tables) }} ) AS previous
    ON previous.topic = source_data.topic
    AND previous.time < source_data.time
WHERE (source_data.total_active_power).TimeStamp != (previous.total_active_power).TimeStamp
OR (source_data.total_power_factor).TimeStamp != (previous.total_power_factor).TimeStamp
