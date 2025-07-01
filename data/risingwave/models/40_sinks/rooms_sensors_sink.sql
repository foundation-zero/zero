{{ config(materialized='sink') }}
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
{{ sink_upsert_pg_dmc('rooms_sensors', 'id') }}
