{{ config(materialized='materialized_view') }}
SELECT 
	bms_master.topic,
	bms_master.time,
	(bms_master."Stored_Power").value AS stored_power,
	(bms_master."Stored_Power").TimeStamp AS stored_power_timestamp,
	(bms_master."Stored_Energy").value AS stored_energy,
	(bms_master."Stored_Energy").TimeStamp AS stored_energy_timestamp
FROM {{ ref('bms_master') }} AS bms_master
ASOF JOIN {{ ref('bms_master') }} AS previous
    ON previous.topic = bms_master.topic
    AND previous.time < bms_master.time
WHERE (bms_master."Stored_Power").TimeStamp != (previous."Stored_Power").TimeStamp
OR (bms_master."Stored_Energy").TimeStamp != (previous."Stored_Energy").TimeStamp
