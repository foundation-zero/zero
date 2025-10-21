{{ config(materialized='materialized_view') }}

{%- set tables = ['power_tag', 'pvt', 'shore_power', 'hydrogeneration'] -%}

WITH combined_power_data AS (
	{%- for t in tables -%}
  		SELECT
    		{{ t }}.topic,
			{{ t }}.time,
			{{ t }}."Total_Active_Power",
			{{ t }}."Total_Power_Factor"
  		FROM {{ ref(t) }} AS {{ t }}
	{%- if not loop.last %} UNION ALL {% endif %}
	{%- endfor -%}
)

{{ filter_marpower_topic_changes(
    'combined_power_data', {
        'Total_Active_Power' : ('active_power', 'active_power_timestamp'),
        'Total_Power_Factor' : ('power_factor', 'power_factor_timestamp')
    })
}}
