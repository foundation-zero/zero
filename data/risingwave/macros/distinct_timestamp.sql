{% macro distinct_timestamp(table_name, fields_with_values) %}
SELECT 
    {{ table_name }}.topic,
    {{ table_name }}.time,

    {% for field_name, value in fields_with_values.items() %}
        ({{ table_name }}.{{ '"' ~ field_name ~ '"' }}).value AS {{ value[0] }},
        ({{ table_name }}.{{ '"' ~ field_name ~ '"' }}).TimeStamp AS {{ value[1] }}
    {% if not loop.last %}, {% endif %}
    {% endfor %}

FROM {{ table_name }}
ASOF JOIN {{ table_name }} AS previous
  ON previous.topic = {{ table_name }}.topic
  AND previous.time < {{ table_name }}.time

WHERE

    {% for field_name in fields_with_values %}
	    ({{ table_name }}.{{ '"' ~ field_name ~ '"' }}).TimeStamp != (previous.{{ '"' ~ field_name ~ '"' }}).TimeStamp
    {% if not loop.last %}OR {% endif %}
    {% endfor %}

{% endmacro %}
