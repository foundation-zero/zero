{% macro get_marpower_power_data(tables) %}

{%- for t in tables -%}
  SELECT
    {{ t }}.topic,
		{{ t }}.time,
		{{ t }}."Total_Active_Power" AS total_active_power,
		{{ t }}."Total_Power_Factor" AS total_power_factor
  FROM {{ ref(t) }} AS {{ t }}
{%- if not loop.last %} UNION ALL {% endif %}
{%- endfor -%}

{% endmacro %}
