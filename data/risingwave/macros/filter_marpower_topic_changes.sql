{% macro filter_marpower_topic_changes(table_ref, fields_with_values) -%}

SELECT 
    marpower_data.topic,
    marpower_data.time,

    {%- for field_name, value in fields_with_values.items() %}
    (marpower_data.{{ '"' ~ field_name ~ '"' }}).value AS {{ value[0] }},
    (marpower_data.{{ '"' ~ field_name ~ '"' }}).TimeStamp AS {{ value[1] }}
    {%- if not loop.last -%}, {% endif %}
    {%- endfor %}

FROM {{ table_ref }} AS marpower_data
ASOF JOIN {{ table_ref }} AS previous
  ON previous.topic = marpower_data.topic
  AND previous.time < marpower_data.time

WHERE
    {%- for field_name in fields_with_values %}
	(marpower_data.{{ '"' ~ field_name ~ '"' }}).TimeStamp > (previous.{{ '"' ~ field_name ~ '"' }}).TimeStamp
    {%- if not loop.last %} OR {% endif %}
    {%- endfor -%}

{% endmacro %}
