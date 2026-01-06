{{ config(materialized='materialized_view') }}

WITH power_updates AS (
    SELECT
        topic,
        time,
        current * voltage / 1000 AS power,
        GREATEST(curr_timestamp, voltage_timestamp) AS power_timestamp
    FROM (
        SELECT
            consumers.topic,
            consumers.time,
            consumers."current",
            consumers.curr_timestamp,
            system_voltages.voltage,
            system_voltages.voltage_timestamp
        FROM {{ ref('24v_current_updates')}} consumers
        ASOF JOIN {{ ref('24v_system_voltage_data')}} system_voltages
            ON system_voltages.system_code = regexp_match(consumers.topic, '/24(e\w+)_')[1]
            AND system_voltages.time <= consumers.time
    )
)
    
{{ join_electrical_metadata('power_updates') }}
