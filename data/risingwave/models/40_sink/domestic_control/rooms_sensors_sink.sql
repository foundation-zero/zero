CREATE SINK {{ this }} AS (
  SELECT
    "id",
    "room_id",
    "name",
    "type",
    "value",
    "time"
  FROM
    {{ ref('rooms_sensors') }}
)
{{ sink_upsert_pg('rooms_sensors', 'id', 'domestic_control') }}
