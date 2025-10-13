{{ config(materialized='materialized_view') }}
SELECT 
  bms_master_updates.stored_power AS stored_power,
  bms_master_updates.stored_power_timestamp AS stored_power_timestamp,
  bms_master_updates.stored_energy AS stored_energy,
  bms_master_updates.stored_energy_timestamp AS stored_energy_timestamp,
  bms_master_updates.topic AS topic,
  metadata.electrical_system AS electrical_system,
  metadata.group AS group_name
FROM {{ ref('bms_master_updates') }} AS bms_master_updates
JOIN {{ ref('electrical_energy_metadata') }} AS metadata ON bms_master_updates.topic = metadata.preferred_mqtt_topic
