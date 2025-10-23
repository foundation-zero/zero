{% macro filter_marpower_topic_changes(table_alias, fields_with_values) -%}

SELECT 
    {{ table_alias }}.topic,
    {{ table_alias }}.time,

    {%- for field_name, value in fields_with_values.items() %}
    ({{ table_alias }}.{{ '"' ~ field_name ~ '"' }}).value AS {{ value[0] }},
    ({{ table_alias }}.{{ '"' ~ field_name ~ '"' }}).TimeStamp AS {{ value[1] }}
    {%- if not loop.last -%}, {% endif %}
    {%- endfor %}

FROM {{ table_alias }}
ASOF JOIN {{ table_alias }} AS previous
  ON previous.topic = {{ table_alias }}.topic
  AND previous.time < {{ table_alias }}.time

WHERE

    {%- for field_name in fields_with_values %}
	({{ table_alias }}.{{ '"' ~ field_name ~ '"' }}).TimeStamp != (previous.{{ '"' ~ field_name ~ '"' }}).TimeStamp
    {%- if not loop.last %} OR {% endif %}
    {%- endfor -%}

{% endmacro %}
