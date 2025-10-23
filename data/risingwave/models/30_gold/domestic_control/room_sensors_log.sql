SELECT
    logs.id,
    sensors.room_id,
    logs.type,
    logs.time,
    logs.value,
    sensors.name
FROM
    {{ ref('ac_sensors_pivot')}} as logs
LEFT JOIN {{ ref('sensors') }} sensors ON sensors.id = logs.id
