{{ config(materialized='materialized_view') }}
SELECT 
  power_updates.active_power AS active_power,
  power_updates.active_power_timestamp AS active_power_timestamp,
  power_updates.power_factor AS power_factor,
  power_updates.power_factor_timestamp AS power_factor_timestamp,
  power_updates.topic AS topic,
  producers.electrical_system AS electrical_system,
  producers.group AS consumer_group
FROM {{ ref('pvt_power_updates') }} AS power_updates
JOIN {{ ref('power_tag_metadata') }} AS producers ON power_updates.topic = producers.preferred_mqtt_topic
