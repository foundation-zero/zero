SELECT
    "id",
    "room_id",
    "name",
    "type",
    "value",
    "time"
FROM  {{ ref('room_sensors_log') }}
WHERE row_num = 1;
