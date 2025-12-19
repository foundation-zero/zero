{{ config(materialized='materialized_view') }}

WITH power_updates AS (
    SELECT
        topic,
        time,
        current * voltage / 1000 AS power,
        greatest("curr_timestamp", volt_timestamp) as power_timestamp
    FROM {{ ref('24v_power_updates') }}
)

{{ join_electrical_metadata('power_updates') }}
