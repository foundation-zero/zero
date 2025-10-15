{{ config(materialized='materialized_view') }}
SELECT 
	battery_dc_converter.topic,
	battery_dc_converter.time,
	(battery_dc_converter."Voltage_A").value AS voltage_a,
	(battery_dc_converter."Voltage_A").TimeStamp AS voltage_a_timestamp,
	(battery_dc_converter."Voltage_B").value AS voltage_b,
	(battery_dc_converter."Voltage_B").TimeStamp AS voltage_b_timestamp,
	(battery_dc_converter."Current_A").value AS current_a,
	(battery_dc_converter."Current_A").TimeStamp AS current_a_timestamp,
	(battery_dc_converter."Current_B").value AS current_b,
	(battery_dc_converter."Current_B").TimeStamp AS current_b_timestamp
FROM {{ ref('battery_dc_converter') }} AS battery_dc_converter
ASOF JOIN {{ ref('battery_dc_converter') }} AS previous
    ON previous.topic = battery_dc_converter.topic
    AND previous.time < battery_dc_converter.time
WHERE (battery_dc_converter."Voltage_A").TimeStamp != (previous."Voltage_A").TimeStamp
OR (battery_dc_converter."Voltage_B").TimeStamp != (previous."Voltage_B").TimeStamp
OR (battery_dc_converter."Current_A").TimeStamp != (previous."Current_A").TimeStamp
OR (battery_dc_converter."Current_B").TimeStamp != (previous."Current_B").TimeStamp
