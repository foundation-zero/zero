{{ config(materialized='materialized_view') }}
SELECT
    MAX(timestamp) AS timestamp,
    group_name,
    SUM(avg_power) AS group_power
FROM
(
	-- Consumer and producer power data
	SELECT
		MAX(electrical_power_data.time) AS timestamp,
		electrical_power_data.group_name AS group_name,
		AVG(electrical_power_data.active_power) AS avg_power
	FROM {{ ref('consumer_producer_power_data') }} AS electrical_power_data
	WHERE
		electrical_power_data.group_name IS NOT NULL
		AND electrical_power_data.time > NOW() - INTERVAL '5 minutes'
	GROUP BY topic, group_name
	
	UNION ALL
	
	-- Charging / discharging power data
	SELECT
		MAX(electrical_charging_data.time) AS timestamp,
		electrical_charging_data.group_name AS group_name,
		AVG(electrical_charging_data.voltage_a) * AVG(electrical_charging_data.current_a) AS avg_power
	FROM {{ ref('battery_dc_converter_power_data') }}  AS electrical_charging_data
	WHERE
		electrical_charging_data.group_name IS NOT NULL
		AND electrical_charging_data.time > NOW() - INTERVAL '5 minutes'
	GROUP BY topic, group_name
)
GROUP BY group_name
