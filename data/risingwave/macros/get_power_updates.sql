{% macro get_power_updates(table_name, field_names) -%}
SELECT 
	power_data.topic,
	power_data.time,

  {%- for f in field_names -%}
    (power_data.{{ '"' ~ f ~ '"' }}).value AS {{ f | lower }},
    (power_data.{{ '"' ~ f ~ '"' }}).TimeStamp AS {{ f ~'_timestamp' | lower }}
  {%- if not loop.last %},{% endif %}
  {% endfor %}

FROM {{ ref(table_name) }} AS power_data
ASOF JOIN {{ ref(table_name) }} AS previous 
  ON previous.topic = power_data.topic
  AND previous.time < power_data.time
WHERE 
  
  {%- for f in field_names -%}
	  (power_data.{{ '"' ~ f ~ '"' }}).TimeStamp != (previous.{{ '"' ~ f ~ '"' }}).TimeStamp
  {% if not loop.last %}OR {% endif -%}
  {% endfor %}

{%- endmacro %}
