{{ config(materialized='materialized_view') }}
SELECT
    MAX(time_stamp) AS power_timestamp,
    consumer_group AS group_name,
    SUM(active_power) AS power,
    NULL as power_stored                    /* Used for battery data only */
FROM
(
	SELECT
        ROW_NUMBER()
        	OVER (PARTITION BY electrical_consumption.topic
	        ORDER BY GREATEST(electrical_consumption.active_power_timestamp, electrical_consumption.power_factor_timestamp) DESC) AS rn,
        electrical_consumption.topic,
        electrical_consumption.consumer_group,
        electrical_consumption.active_power,
        electrical_consumption.power_factor,
        electrical_consumption.active_power_timestamp AS time_stamp
	FROM {{ ref('electrical_consumption') }} AS electrical_consumption
	WHERE electrical_consumption.consumer_group IS NOT NULL
)
WHERE rn = 1
GROUP BY group_name
ORDER BY group_name