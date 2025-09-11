{{ config(materialized='materialized_view') }}
SELECT 
  power_updates.active_power AS active_power,
  power_updates.active_power_timestamp AS active_power_timestamp,
  power_updates.power_factor AS power_factor,
  power_updates.power_factor_timestamp AS power_factor_timestamp,
  power_updates.topic AS topic,
  consumers.electrical_system AS electrical_system,
  consumers.group AS consumer_group
FROM {{ ref('power_tag_power_updates') }} AS power_updates
JOIN {{ ref('power_tag_metadata') }} AS consumers ON power_updates.topic = consumers.preferred_mqtt_topic
