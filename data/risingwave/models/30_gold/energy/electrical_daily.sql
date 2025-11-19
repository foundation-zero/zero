{{ config(materialized='materialized_view') }}
SELECT
    electrical_system,
    group_name,
    sub_group_name,
    topic,
    date_trunc('day', hour) AS day,
    SUM(energy_wh) AS energy_wh
FROM {{ ref('electrical_hourly') }}
GROUP BY
    electrical_system,
    group_name,
    sub_group_name,
    topic,
    day
