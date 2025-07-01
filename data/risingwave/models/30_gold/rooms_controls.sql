{{ config(materialized='materialized_view') }}
SELECT
    "id",
    "room_id",
    "name",
    "type",
    "value",
    "time"
FROM  {{ ref('rooms_controls_log') }}
WHERE row_num = 1;
