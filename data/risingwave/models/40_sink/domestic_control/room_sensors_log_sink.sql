CREATE SINK {{ this }} FROM {{ ref('room_sensors_log') }}
{{ sink_append_pg('room_sensors_log', 'zero', 'domestic') }}
