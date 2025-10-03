{{ config(materialized='materialized_view') }}
SELECT 
  power_updates.active_power AS active_power,
  power_updates.active_power_timestamp AS active_power_timestamp,
  power_updates.power_factor AS power_factor,
  power_updates.power_factor_timestamp AS power_factor_timestamp,
  power_updates.topic AS topic,
  meta_data.electrical_system AS electrical_system,
  meta_data.group AS consumer_group
FROM (

  SELECT 
    pvt.active_power AS active_power,
    pvt.active_power_timestamp AS active_power_timestamp,
    pvt.power_factor AS power_factor,
    pvt.power_factor_timestamp AS power_factor_timestamp,
    pvt.topic AS topic
  FROM {{ ref('pvt_power_updates') }} AS pvt

UNION

  SELECT 
    shore.active_power AS active_power,
    shore.active_power_timestamp AS active_power_timestamp,
    shore.power_factor AS power_factor,
    shore.power_factor_timestamp AS power_factor_timestamp,
    shore.topic AS topic
  FROM {{ ref('shore_power_power_updates') }} AS shore

UNION

  SELECT 
    hydro.active_power AS active_power,
    hydro.active_power_timestamp AS active_power_timestamp,
    hydro.power_factor AS power_factor,
    hydro.power_factor_timestamp AS power_factor_timestamp,
    hydro.topic AS topic
  FROM {{ ref('hydrogeneration_power_updates') }} AS hydro

) AS power_updates
JOIN {{ ref('electrical_energy_metadata') }} AS meta_data ON power_updates.topic = meta_data.preferred_mqtt_topic
