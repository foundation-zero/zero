SELECT
    CONCAT(ac.id, '/control/temperature') AS "id",
    ac.time AS "time",
    'temperature' AS "type",
    ac.temperature_setpoint AS "value"
FROM {{ ref('ac_update') }} AS ac
WHERE temperature_setpoint IS NOT NULL
UNION ALL
SELECT
    CONCAT(ac.id, '/control/humidity') AS "id",
    ac.time AS "time",
    'humidity' AS "type",
    ac.humidity_setpoint AS "value"
FROM {{ ref('ac_update') }} AS ac
WHERE humidity_setpoint IS NOT NULL
UNION ALL
SELECT
    CONCAT(ac.id, '/control/co2') AS "id",
    ac.time AS "time",
    'co2' AS "type",
    ac.co2_setpoint AS "value"
FROM {{ ref('ac_update') }} AS ac
WHERE co2_setpoint IS NOT NULL;
