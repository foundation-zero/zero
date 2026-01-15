{% macro join_electrical_metadata(table_ref) -%}

SELECT 
    power_data.*,
    metadata.electrical_system AS electrical_system,
    metadata.group AS group_name,
    CASE
	    WHEN metadata.group = 'Domestic' THEN COALESCE(metadata.domestic, 'Unknown')
	    WHEN metadata.group = 'HVAC' THEN COALESCE(metadata.hvac, 'Unknown')
	    WHEN metadata.group = 'Technical' THEN COALESCE(metadata.technical, 'Unknown')
	    WHEN metadata.group = 'Propulsion' THEN 'Propulsion'
	    ELSE NULL
	END AS sub_group_name
FROM {{ table_ref }} AS power_data
JOIN {{ ref('electrical_energy_metadata') }} AS metadata ON power_data.topic = metadata.preferred_mqtt_topic

{%- endmacro %}
