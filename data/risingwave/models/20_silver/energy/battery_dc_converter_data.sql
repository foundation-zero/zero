{{ config(materialized='materialized_view') }}
SELECT 
  battery_dc_converter_updates.voltage_a AS voltage_a,
  battery_dc_converter_updates.voltage_a_timestamp AS voltage_a_timestamp,
  battery_dc_converter_updates.Voltage_b AS Voltage_b,
  battery_dc_converter_updates.Voltage_b_timestamp AS Voltage_b_timestamp,
  battery_dc_converter_updates.current_a AS current_a,
  battery_dc_converter_updates.current_a_timestamp AS current_a_timestamp,
  battery_dc_converter_updates.current_b AS current_b,
  battery_dc_converter_updates.current_b_timestamp AS current_b_timestamp,
  battery_dc_converter_updates.topic AS topic,
  metadata.electrical_system AS electrical_system,
  metadata.group AS group_name
FROM {{ ref('battery_dc_converter_updates') }} AS battery_dc_converter_updates
JOIN {{ ref('electrical_energy_metadata') }} AS metadata ON battery_dc_converter_updates.topic = metadata.preferred_mqtt_topic
