CREATE SINK {{ this }} AS (
  SELECT
    "id",
    "room_id",
    "name",
    "type",
    "value",
    "time"
  FROM
    {{ ref('room_sensors_log') }}
)
{{ sink_append_pg('room_sensors_log', 'zero', 'domestic') }}
