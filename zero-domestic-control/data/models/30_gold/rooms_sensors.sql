{{ config(materialized='materialized_view') }}
SELECT
    "id",
    "room_id",
    "name",
    "type",
    "value",
    "time"
FROM  {{ ref('rooms_sensors_log') }}
WHERE row_num = 1;
