{% macro marpower_power_updates(source) %}
  {{ config(materialized='materialized_view', alias=source ~ '_power_updates') }}
  SELECT
    source_data.topic,
    source_data.time,
    (source_data."Total_Active_Power")."Value" AS active_power,
    (source_data."Total_Active_Power").TimeStamp AS active_power_timestamp,
    (source_data."Total_Power_Factor")."Value" AS power_factor,
    (source_data."Total_Power_Factor").TimeStamp AS power_factor_timestamp
  FROM {{ ref(source) }} AS source_data
  ASOF JOIN {{ ref(source) }} as previous
    ON previous.topic = source_data.topic
    AND previous.time < source_data.time
  WHERE (source_data."Total_Active_Power").TimeStamp != (previous."Total_Active_Power").TimeStamp
    OR (source_data."Total_Power_Factor").TimeStamp != (previous."Total_Power_Factor").TimeStamp
{%- endmacro %}
