{{ config(materialized='materialized_view') }}
SELECT
    MAX(timestamp) AS timestamp,
    group_name,
    AVG(avg_power) AS avg_group_power,
    NULL as power_stored                    /* Used for battery data only */
FROM
(
	SELECT
		MAX(electrical_consumption.active_power_timestamp) AS timestamp,
		electrical_consumption.consumer_group AS group_name,
		AVG(electrical_consumption.active_power) AS avg_power
	FROM public.electrical_consumption AS electrical_consumption
	WHERE
		electrical_consumption.consumer_group IS NOT NULL
		AND electrical_consumption.active_power_timestamp > NOW() - INTERVAL '5 minutes'
	GROUP BY topic, group_name
)
GROUP BY group_name
