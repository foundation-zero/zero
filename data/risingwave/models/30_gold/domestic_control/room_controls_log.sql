SELECT
    logs.id,
    conditions.room_id,
    conditions.name,
    logs.type,
    logs.value,
    logs.time
FROM
    {{ ref('ac_controls_pivot')}} as logs
LEFT JOIN {{ ref('conditions') }} conditions ON logs.id = conditions.id
UNION ALL
SELECT
    amplifiers.id,
    logs.id as "room_id",
    amplifiers.name,
    'amplifier' as "type",
    CAST(logs.is_on AS INT) as "value",
    logs.time
FROM
    {{ ref('amplifiers_update') }} as logs
LEFT JOIN {{ ref('amplifiers') }} amplifiers ON logs.id = amplifiers.room_id
UNION ALL
SELECT
    logs.id,
    blinds.room_id,
    blinds.name,
    'blinds' as "type",
    logs.level as "value",
    logs.time
FROM
    {{ ref('blinds_update') }} as logs
LEFT JOIN {{ ref('blinds') }} blinds ON logs.id = blinds.id
UNION ALL
SELECT
    logs.id,
    lighting_groups.room_id,
    lighting_groups.name,
    'lights' as "type",
    logs.level as "value",
    logs.time
FROM
    {{ ref('lighting_groups_update') }} as logs
LEFT JOIN {{ ref('lighting_groups') }} lighting_groups ON logs.id = lighting_groups.id
