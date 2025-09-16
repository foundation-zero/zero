{{ config(materialized='materialized_view') }}
SELECT
    topic,
    power_hour,
    power_wh
FROM
(
    -- Select electrical consumption per topic, per hour for all completed hours (not including running hour)
    SELECT
        electrical_consumption.topic AS topic,
        TO_TIMESTAMP(FLOOR(EXTRACT(EPOCH FROM electrical_consumption.active_power_timestamp) / 3600) * 3600) AS power_hour,

        -- Calculate average power (Wh) over proportional hours: if hour contains only measurements of a part of the hour, the average power is diveded proportionally
        AVG(electrical_consumption.active_power) * (MAX(date_part('minute', electrical_consumption.active_power_timestamp)) - MIN(date_part('minute',electrical_consumption.active_power_timestamp)) + 1) / 60.0
            AS power_wh
    FROM
        {{ ref('electrical_consumption') }} AS electrical_consumption
    WHERE
        TO_TIMESTAMP(FLOOR(EXTRACT(EPOCH FROM electrical_consumption.active_power_timestamp) / 3600) * 3600) < NOW() - INTERVAL '1 hour'
    GROUP BY
        topic,
        power_hour
    
    UNION ALL
    
    -- Select electrical consumption per topic, per hour for running hour
    SELECT
        electrical_consumption.topic AS topic,
        TO_TIMESTAMP(FLOOR(EXTRACT(EPOCH FROM electrical_consumption.active_power_timestamp) / 3600) * 3600) AS power_hour,

        -- Calculate average power (Wh) for running hour: if measurements started later than the start of the hour, the average power is divided proportionally
        AVG(electrical_consumption.active_power) * (60 - MIN(date_part('minute',electrical_consumption.active_power_timestamp))) / 60.0 AS power_wh
    FROM
        {{ ref('electrical_consumption') }} AS electrical_consumption
    WHERE
        TO_TIMESTAMP(FLOOR(EXTRACT(EPOCH FROM electrical_consumption.active_power_timestamp) / 3600) * 3600) >= NOW() - INTERVAL '1 hour'
    GROUP BY
        topic,
        power_hour
)