{{ config(materialized='materialized_view') }}
SELECT
	LAST_VALUE(time ORDER BY time) AS time,
	electrical_system,
	group_name,
	topic,
	LAST_VALUE(stored_energy ORDER BY time) AS stored_energy
FROM {{ ref('bms_master_power_data') }}
WHERE stored_energy IS NOT NULL
GROUP BY electrical_system, group_name, topic
