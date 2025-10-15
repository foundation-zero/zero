{{ config(materialized='materialized_view') }}
{%- set tables = ['power_tag', 'pvt', 'shore_power', 'hydrogeneration'] -%}

WITH combined_power_data AS (
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

SELECT 
	power_data.topic,
	power_data.time,
	(power_data.total_active_power).value AS active_power,
	(power_data.total_active_power).TimeStamp AS active_power_timestamp,
	(power_data.total_active_power).value AS power_factor,
	(power_data.total_active_power).TimeStamp AS power_factor_timestamp
FROM combined_power_data AS power_data
ASOF JOIN combined_power_data AS previous
    ON previous.topic = power_data.topic
    AND previous.time < power_data.time
WHERE (power_data.total_active_power).TimeStamp != (previous.total_active_power).TimeStamp
OR (power_data.total_power_factor).TimeStamp != (previous.total_power_factor).TimeStamp
