{{ config(materialized='materialized_view') }}
SELECT 
  power_updates.active_power AS active_power,
  power_updates.active_power_timestamp AS active_power_timestamp,
  power_updates.power_factor AS power_factor,
  power_updates.power_factor_timestamp AS power_factor_timestamp,
  power_updates.topic AS topic,
  metadata.electrical_system AS electrical_system,
  metadata.group AS group_name
FROM {{ ref('power_updates') }} AS power_updates
JOIN {{ ref('electrical_energy_metadata') }} AS metadata ON power_updates.topic = metadata.preferred_mqtt_topic
