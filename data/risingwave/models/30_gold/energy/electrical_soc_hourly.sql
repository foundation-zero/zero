{{ config(materialized='materialized_view') }}

-- Calculate stored energy (Wh) by calculating average values per minute to determine which minutes have data.
-- The energy value is then summed up and divided by 60 to go from Watt minutes to Watt hours.
WITH per_minute AS (
    SELECT
        soc_data.electrical_system AS electrical_system,
        soc_data.group_name AS group_name,
        soc_data.sub_group_name AS sub_group_name,
        soc_data.topic AS topic,
        window_start AS min_start,
        AVG(soc_data.stored_energy) AS avg_soc
    FROM
    TUMBLE (
        {{ ref('bms_master_power_data') }},
        stored_energy_timestamp,
        INTERVAL '1 MINUTE'
    ) AS soc_data
    GROUP BY
        electrical_system,
        group_name,
        sub_group_name,
        topic,
        window_start
)
SELECT
    electrical_system,
    group_name,
    sub_group_name,
    topic,
    date_trunc('hour', min_start) AS hour,
    SUM(avg_soc) / 60.0 AS soc
FROM per_minute
GROUP BY
    electrical_system,
    group_name,
    sub_group_name,
    topic,
    date_trunc('hour', min_start)
