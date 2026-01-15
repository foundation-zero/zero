{{ config(materialized='materialized_view') }}

{%- set tables = ['power_tag', 'pvt', 'shore_power', 'hydrogeneration'] -%}

-- First iterate over the array of table names to create the CTEs with the update records from the macro
WITH

{% for t in tables -%}
{{ t }}_updates AS (
{{ filter_marpower_topic_changes(
	ref(t), {
		'Total_Active_Power' : ('active_power', 'active_power_timestamp'),
		'Total_Power_Factor' : ('power_factor', 'power_factor_timestamp')
	})
}}
)
{%- if not loop.last %},{% endif %}
{% endfor %}

-- Iterate the array a second time for the SELECT statements which are combined with a UNION
{% for t in tables -%}
SELECT
	topic,
	time,
	active_power,
	active_power_timestamp,
	power_factor,
	power_factor_timestamp
FROM {{ t }}_updates
{% if not loop.last %}UNION ALL{% endif %}
{% endfor -%}
