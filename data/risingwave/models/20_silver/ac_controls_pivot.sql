{{ config(materialized='materialized_view') }}
SELECT
    CONCAT(ac.id, '/control/temperature') as "id",
    ac.time as "time",
    'temperature' AS "type",
    ac.temperature_setpoint AS "value"
FROM {{ ref('ac_update') }} as ac
WHERE temperature_setpoint IS NOT NULL
UNION ALL
SELECT
    CONCAT(ac.id, '/control/humidity') as "id",
    ac.time as "time",
    'humidity' AS "type",
    ac.humidity_setpoint AS "value"
FROM {{ ref('ac_update') }} as ac
WHERE humidity_setpoint IS NOT NULL
UNION ALL
SELECT
    CONCAT(ac.id, '/control/co2') as "id",
    ac.time as "time",
    'co2' AS "type",
    ac.co2_setpoint AS "value"
FROM {{ ref('ac_update') }} as ac
WHERE co2_setpoint IS NOT NULL;
