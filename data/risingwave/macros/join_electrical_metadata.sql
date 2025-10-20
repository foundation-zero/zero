{% macro join_electrical_metadata(table_name) -%}
SELECT 
    updates.*,
    metadata.electrical_system AS electrical_system,
    metadata.group AS group_name
FROM {{ ref(table_name) }} AS updates
JOIN {{ ref('electrical_energy_metadata') }} AS metadata ON updates.topic = metadata.preferred_mqtt_topic
{%- endmacro %}
