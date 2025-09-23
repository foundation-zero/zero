{{ config(materialized='materialized_view') }}
SELECT power_tag.topic,
       power_tag.time,
       (power_tag."Total_Active_Power")."Value" AS active_power,
       (power_tag."Total_Active_Power").TimeStamp AS active_power_timestamp,
       (power_tag."Total_Power_Factor")."Value" AS power_factor,
       (power_tag."Total_Power_Factor").TimeStamp AS power_factor_timestamp
FROM {{ ref('power_tag') }} AS power_tag
ASOF JOIN {{ ref('power_tag') }} as previous
  ON previous.topic = power_tag.topic
    AND previous.time < power_tag.time
WHERE (power_tag."Total_Active_Power").TimeStamp != (previous."Total_Active_Power").TimeStamp
  OR (power_tag."Total_Power_Factor").TimeStamp != (previous."Total_Power_Factor").TimeStamp