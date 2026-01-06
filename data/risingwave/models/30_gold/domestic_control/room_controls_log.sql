SELECT
    logs.id,
    conditions.room_id,
    conditions.name,
    logs.type,
    logs.value,
    logs.time
FROM
    {{ ref('ac_controls_pivot')}} AS logs
LEFT JOIN {{ ref('conditions') }} conditions ON logs.id = conditions.id
UNION ALL
SELECT
    amplifiers.id,
    logs.id AS "room_id",
    amplifiers.name,
    'amplifier' AS "type",
    CAST(logs.is_on AS INT) AS "value",
    logs.time
FROM
    {{ ref('amplifiers_update') }} AS logs
LEFT JOIN {{ ref('amplifiers') }} amplifiers ON logs.id = amplifiers.room_id
UNION ALL
SELECT
    logs.id,
    blinds.room_id,
    blinds.name,
    'blinds' AS "type",
    logs.level AS "value",
    logs.time
FROM
    {{ ref('blinds_update') }} AS logs
LEFT JOIN {{ ref('blinds') }} blinds ON logs.id = blinds.id
UNION ALL
SELECT
    logs.id,
    lighting_groups.room_id,
    lighting_groups.name,
    'lights' AS "type",
    logs.level AS "value",
    logs.time
FROM
    {{ ref('lighting_groups_update') }} AS logs
LEFT JOIN {{ ref('lighting_groups') }} lighting_groups ON logs.id = lighting_groups.id
