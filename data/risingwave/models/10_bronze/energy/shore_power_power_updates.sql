{{ config(materialized='materialized_view') }}
SELECT shore_power.topic,
       shore_power.time,
       (shore_power."Total_Active_Power")."Value" AS active_power,
       (shore_power."Total_Active_Power").TimeStamp AS active_power_timestamp,
       (shore_power."Total_Power_Factor")."Value" AS power_factor,
       (shore_power."Total_Power_Factor").TimeStamp AS power_factor_timestamp
FROM {{ ref('shore_power') }} AS shore_power
ASOF JOIN {{ ref('shore_power') }} as previous
  ON previous.topic = shore_power.topic
    AND previous.time < shore_power.time
WHERE (shore_power."Total_Active_Power").TimeStamp != (previous."Total_Active_Power").TimeStamp
  OR (shore_power."Total_Power_Factor").TimeStamp != (previous."Total_Power_Factor").TimeStamp
