{{ config(materialized='materialized_view') }}
SELECT
	timestamp,
	topic,
	group_name,
	stored_energy
FROM (
	SELECT
		stored_energy_timestamp AS  timestamp,
		topic,
		group_name,
		stored_energy,
		ROW_NUMBER() OVER (PARTITION BY topic ORDER BY stored_energy_timestamp DESC) AS row_nr
	FROM {{ ref('bms_master_power_data') }}
) AS electrical_energy_stored
WHERE row_nr = 1
