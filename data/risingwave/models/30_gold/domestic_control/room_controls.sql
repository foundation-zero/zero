SELECT
    "id",
    "room_id",
    "name",
    "type",
    "value",
    "time"
FROM  {{ ref('room_controls_log') }}
WHERE row_num = 1;
