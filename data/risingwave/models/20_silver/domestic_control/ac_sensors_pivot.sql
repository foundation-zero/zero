SELECT
    CONCAT(ac.id, '/sensor/temperature') as "id",
    ac.time as "time",
    'temperature' AS "type",
    ac.actual_temperature AS "value"
FROM {{ ref('ac_update') }} as ac
WHERE actual_temperature IS NOT NULL
UNION ALL
SELECT
    CONCAT(ac.id, '/sensor/humidity') as "id",
    ac.time as "time",
    'humidity' AS "type",
    ac.actual_humidity AS "value"
FROM {{ ref('ac_update') }} as ac
WHERE actual_humidity IS NOT NULL
UNION ALL
SELECT
    CONCAT(ac.id, '/sensor/co2') as "id",
    ac.time as "time",
    'co2' AS "type",
    ac.actual_co2 AS "value"
FROM {{ ref('ac_update') }} as ac
WHERE actual_co2 IS NOT NULL;
