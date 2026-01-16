{{ config(materialized='materialized_view') }}

SELECT
    electrical_power_data.electrical_system AS electrical_system,
    electrical_power_data.group_name AS group_name,
    electrical_power_data.sub_group_name AS sub_group_name,
    electrical_power_data.topic AS topic,
    window_start AS "minute",
    AVG(electrical_power_data.active_power) AS avg_w
FROM
TUMBLE (
    {{ ref('consumer_producer_power_data') }},
    time,
    INTERVAL '1 MINUTE'
) AS electrical_power_data
GROUP BY
    electrical_system,
    group_name,
    sub_group_name,
    topic,
    window_start
