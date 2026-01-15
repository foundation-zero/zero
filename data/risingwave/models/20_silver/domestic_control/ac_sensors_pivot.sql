SELECT
    CONCAT(ac.id, '/sensor/temperature') AS "id",
    ac.time AS "time",
    'temperature' AS "type",
    ac.actual_temperature AS "value"
FROM {{ ref('ac_update') }} AS ac
WHERE actual_temperature IS NOT NULL
UNION ALL
SELECT
    CONCAT(ac.id, '/sensor/humidity') AS "id",
    ac.time AS "time",
    'humidity' AS "type",
    ac.actual_humidity AS "value"
FROM {{ ref('ac_update') }} AS ac
WHERE actual_humidity IS NOT NULL
UNION ALL
SELECT
    CONCAT(ac.id, '/sensor/co2') AS "id",
    ac.time AS "time",
    'co2' AS "type",
    ac.actual_co2 AS "value"
FROM {{ ref('ac_update') }} AS ac
WHERE actual_co2 IS NOT NULL;
