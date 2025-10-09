{{ config(materialized='materialized_view') }}
{%- set tables = ['power_tag', 'pvt', 'shore_power', 'hydrogeneration'] -%}

-- Create CTE with combined data of all power data tabels
WITH cte AS (
{%- for t in tables -%}
  		SELECT
    	{{ t }}.topic,
			{{ t }}.time,
			{{ t }}."Total_Active_Power" AS total_active_power,
			{{ t }}."Total_Power_Factor" AS total_power_factor
  		FROM {{ ref(t) }} AS {{ t }}
	{%- if not loop.last %} UNION ALL {% endif %}
	{%- endfor -%}
)

-- Get power data updates from CTE.
SELECT 
	source_data.topic,
	source_data.time,
	(source_data.total_active_power).value AS active_power,
	(source_data.total_active_power).TimeStamp AS active_power_timestamp,
	(source_data.total_active_power).value AS power_factor,
	(source_data.total_active_power).TimeStamp AS power_factor_timestamp
FROM cte AS source_data
ASOF JOIN cte AS previous
    ON previous.topic = source_data.topic
    AND previous.time < source_data.time
WHERE (source_data.total_active_power).TimeStamp != (previous.total_active_power).TimeStamp
OR (source_data.total_power_factor).TimeStamp != (previous.total_power_factor).TimeStamp
