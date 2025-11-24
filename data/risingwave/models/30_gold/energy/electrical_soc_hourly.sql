{{ config(materialized='materialized_view') }}

-- Calculate stored energy (Wh) by calculating average values per hour per topic.
SELECT
    soc_data.electrical_system AS electrical_system,
    soc_data.group_name AS group_name,
    soc_data.sub_group_name AS sub_group_name,
    soc_data.topic AS topic,
    window_start AS hour,
    AVG(soc_data.stored_energy) AS soc
FROM
TUMBLE (
    {{ ref('bms_master_power_data') }},
    stored_energy_timestamp,
    INTERVAL '1 HOUR'
) AS soc_data
GROUP BY
    electrical_system,
    group_name,
    sub_group_name,
    topic,
    window_start
