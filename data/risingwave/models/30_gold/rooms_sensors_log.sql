{{ config(materialized='materialized_view') }}
SELECT
    row_number() OVER (PARTITION BY logs.id ORDER BY logs.time DESC) AS row_num,
    logs.id,
    sensors.room_id,
    logs.type,
    logs.time,
    logs.value,
    sensors.name
FROM
    {{ ref('ac_sensors_pivot')}} as logs
LEFT JOIN {{ ref('sensors') }} sensors ON sensors.id = logs.id
