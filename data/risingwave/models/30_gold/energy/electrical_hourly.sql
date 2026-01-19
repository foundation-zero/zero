{{ config(materialized='materialized_view') }}

-- Calculate electrical energy (Wh) of completed hours by dividing the sum of the average electrical energy per minute by the amount of minutes in the hour.
-- Any gaps in an hour result in a lower energy value, but for hours that started later or are not finished yet (current hour) the energy value is extrapolated.
SELECT
    electrical_system,
    group_name,
    sub_group_name,
    topic,
    date_trunc('hour', "minute") AS "hour",
    SUM(avg_w) / (MAX(date_part('minute', "minute")) - MIN(date_part('minute', "minute")) + 1) AS energy_wh
FROM {{ ref('electrical_per_minute') }}
GROUP BY
    electrical_system,
    group_name,
    sub_group_name,
    topic,
    date_trunc('hour', "minute")
