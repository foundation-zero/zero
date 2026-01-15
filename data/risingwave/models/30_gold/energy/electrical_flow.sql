{{ config(materialized='materialized_view') }}
SELECT
    MAX(time) AS time,
    electrical_system,
    group_name,
    sub_group_name,
    SUM(avg_power) AS group_power
FROM
(
	-- Consumer and producer power data
	SELECT
		MAX(electrical_power_data.time) AS time,
		electrical_power_data.electrical_system AS electrical_system,
		electrical_power_data.group_name AS group_name,
		electrical_power_data.sub_group_name AS sub_group_name,
		AVG(electrical_power_data.active_power) AS avg_power
	FROM HOP (
		{{ ref('consumer_producer_power_data') }} ,
		time,
		INTERVAL '15 seconds',
		INTERVAL '5 minutes'
	) AS electrical_power_data
	WHERE electrical_power_data.group_name IS NOT NULL
	GROUP BY electrical_system, group_name, sub_group_name, topic

	UNION ALL
	
	-- Charging / discharging power data
	SELECT
		MAX(electrical_charging_data.time) AS time,
		electrical_charging_data.electrical_system AS electrical_system,
		electrical_charging_data.group_name AS group_name,
		electrical_charging_data.sub_group_name AS sub_group_name,
		AVG(electrical_charging_data.voltage_a) * AVG(electrical_charging_data.current_a) AS avg_power
	FROM HOP (
		{{ ref('battery_dc_converter_power_data') }} ,
		time,
		INTERVAL '15 seconds',
		INTERVAL '5 minutes'
	) AS electrical_charging_data
	WHERE electrical_charging_data.group_name IS NOT NULL
	GROUP BY electrical_system, group_name, sub_group_name, topic
)
GROUP BY electrical_system, group_name, sub_group_name
