CREATE SINK {{ this }} FROM {{ ref('room_controls_log') }}
{{ sink_upsert_pg('room_sensors', 'id', 'zero', 'domestic') }}
