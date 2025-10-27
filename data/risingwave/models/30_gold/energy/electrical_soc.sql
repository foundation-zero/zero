{{ config(materialized='materialized_view') }}
SELECT
	LAST_VALUE(time ORDER BY time) AS time,
	topic,
	group_name,
	LAST_VALUE(stored_energy ORDER BY time) AS stored_energy
FROM {{ ref('bms_master_power_data') }}
GROUP BY topic, group_name
