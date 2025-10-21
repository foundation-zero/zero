{{ config(materialized='materialized_view') }}
SELECT
    MAX(timestamp) AS timestamp,
    group_name,
    SUM(avg_power) AS avg_group_power
FROM
(
	SELECT
		MAX(electrical_power_data.active_power_timestamp) AS timestamp,
		electrical_power_data.group_name AS group_name,
		AVG(electrical_power_data.active_power) AS avg_power
	FROM {{ ref('consumer_producer_power_data') }} AS electrical_power_data
	WHERE
		electrical_power_data.group_name IS NOT NULL
		AND electrical_power_data.active_power_timestamp > NOW() - INTERVAL '5 minutes'
	GROUP BY topic, group_name
)
GROUP BY group_name
