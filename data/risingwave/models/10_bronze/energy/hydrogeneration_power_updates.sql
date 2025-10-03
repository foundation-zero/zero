{{ config(materialized='materialized_view') }}
SELECT hydrogeneration.topic,
       hydrogeneration.time,
       (hydrogeneration."Total_Active_Power")."Value" AS active_power,
       (hydrogeneration."Total_Active_Power").TimeStamp AS active_power_timestamp,
       (hydrogeneration."Total_Power_Factor")."Value" AS power_factor,
       (hydrogeneration."Total_Power_Factor").TimeStamp AS power_factor_timestamp
FROM {{ ref('hydrogeneration') }} AS hydrogeneration
ASOF JOIN {{ ref('hydrogeneration') }} as previous
  ON previous.topic = hydrogeneration.topic
    AND previous.time < hydrogeneration.time
WHERE (hydrogeneration."Total_Active_Power").TimeStamp != (previous."Total_Active_Power").TimeStamp
  OR (hydrogeneration."Total_Power_Factor").TimeStamp != (previous."Total_Power_Factor").TimeStamp