{{ config(materialized='materialized_view') }}
SELECT
    topic,
    hour,
    energy_wh
FROM ( (
    -- Calculate energy (Wh) of completed hours (not current hour) proportionally by calculating average values per minute to determine which minutes have data.
    -- The energy value is then summed up and divided by 60 to go from Watt minutes to Watt hours.
    WITH per_minute AS (
        SELECT
            electrical_power_data.topic AS topic,
            window_start AS min_start,
            AVG(electrical_power_data.active_power) AS avg_w
        FROM
        TUMBLE (
            {{ ref('consumer_power_data') }},
            active_power_timestamp,
            INTERVAL '1 MINUTE'
        ) AS electrical_power_data
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
    -- The average energy values are then extrapolated to the expected amount of minutes that will contain data when the hour has passed.
    -- For instance, if there are 10 minutes of data after 30 minutes have passed, we expect to have 40 minutes of data when the hour 
    -- is completely passed. The average value per minute is then extrapolated to 40 minutes and divided by 60.
    WITH per_minute AS (
        SELECT
            electrical_power_data.topic AS topic,
            window_start AS min_start,
            AVG(electrical_power_data.active_power) AS avg_w
        FROM
        TUMBLE (
            {{ ref('consumer_power_data') }},
            active_power_timestamp,
            INTERVAL '1 MINUTE'
        ) AS electrical_power_data
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
