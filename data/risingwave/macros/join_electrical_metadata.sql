{% macro join_electrical_metadata(table_alias) -%}

SELECT 
    {{ table_alias }}.*,
    metadata.electrical_system AS electrical_system,
    metadata.group AS group_name
FROM {{ table_alias }}
JOIN {{ ref('electrical_energy_metadata') }} AS metadata ON {{ table_alias }}.topic = metadata.preferred_mqtt_topic

{%- endmacro %}
