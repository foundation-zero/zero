{{ config(materialized='materialized_view') }}
SELECT 
  power_updates.active_power AS active_power,
  power_updates.active_power_timestamp AS active_power_timestamp,
  power_updates.power_factor AS power_factor,
  power_updates.power_factor_timestamp AS power_factor_timestamp,
  power_updates.topic AS topic,
  meta_data.electrical_system AS electrical_system,
  meta_data.group AS consumer_group
FROM {{ ref('power_updates') }} AS power_updates
JOIN {{ ref('electrical_energy_metadata') }} AS meta_data ON power_updates.topic = meta_data.preferred_mqtt_topic
