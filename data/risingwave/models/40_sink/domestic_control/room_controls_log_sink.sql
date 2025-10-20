CREATE SINK {{ this }} AS (
  SELECT
    "id",
    "room_id",
    "name",
    "type",
    "value",
    "time"
  FROM
    {{ ref('room_controls_log') }}
)
{{ sink_append_pg('room_controls_log', 'zero', 'domestic') }}
