CREATE SINK {{ this }} FROM {{ ref('room_sensors') }}
{{ sink_upsert_pg('room_sensors', 'id', 'zero', 'domestic') }}
