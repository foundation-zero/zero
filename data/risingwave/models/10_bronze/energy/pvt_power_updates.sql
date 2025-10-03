{{ config(materialized='materialized_view') }}
SELECT pvt.topic,
       pvt.time,
       (pvt."Total_Active_Power")."Value" AS active_power,
       (pvt."Total_Active_Power").TimeStamp AS active_power_timestamp,
       (pvt."Total_Power_Factor")."Value" AS power_factor,
       (pvt."Total_Power_Factor").TimeStamp AS power_factor_timestamp
FROM {{ ref('pvt') }} AS pvt
ASOF JOIN {{ ref('pvt') }} as previous
  ON previous.topic = pvt.topic
    AND previous.time < pvt.time
WHERE (pvt."Total_Active_Power").TimeStamp != (previous."Total_Active_Power").TimeStamp
  OR (pvt."Total_Power_Factor").TimeStamp != (previous."Total_Power_Factor").TimeStamp
  