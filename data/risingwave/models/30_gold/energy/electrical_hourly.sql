{{ config(materialized='materialized_view') }}
SELECT
    topic,
    hour,
    energy_wh
FROM ( (
    -- Calculate energy (Wh) of completed hours (not current hour) proportionally by calculating average values per minute to determine which minutes have data.
    -- The energy value is then extrapolated to the total amount of minutes in the hour.
    WITH per_minute AS (
        SELECT
            electrical_consumption.topic AS topic,
            window_start AS min_start,
            AVG(electrical_consumption.active_power) AS avg_w
        FROM
        TUMBLE (
            {{ ref('electrical_consumption') }},
            active_power_timestamp,
            INTERVAL '1 MINUTE'
        ) AS electrical_consumption
        GROUP BY
          topic,
          window_start
    )
    SELECT
        topic,  
        date_trunc('hour', min_start) AS hour,
        SUM(avg_w) / 60.0 AS energy_wh
    FROM per_minute
    WHERE min_start < date_trunc('hour', NOW())
    GROUP BY
        topic,
        date_trunc('hour', min_start)
    )

    UNION ALL (
      
    -- Calculate energy (Wh) of current hour proportionally by calculating average values per minute to determine which minutes have data.
    -- The energy is then extrapolated to the total amount of minutes passed in the current hour.
    WITH per_minute AS (
        SELECT
            electrical_consumption.topic AS topic,
            window_start AS min_start,
            AVG(electrical_consumption.active_power) AS avg_w
        FROM
        TUMBLE (
            {{ ref('electrical_consumption') }},
            active_power_timestamp,
            INTERVAL '1 MINUTE'
        ) AS electrical_consumption
        GROUP BY
            topic,
            window_start
    )
    SELECT
        topic,
        date_trunc('hour', min_start) AS hour,
        AVG(avg_w) * (60 + count() - extract(MINUTE from MAX(min_start)) - 1) / 60 AS energy_wh
    FROM per_minute
    WHERE min_start >= date_trunc('hour', NOW())
    GROUP BY
        topic,
        date_trunc('hour', min_start)
    )
)
