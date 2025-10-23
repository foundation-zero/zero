CREATE SINK {{ this }} FROM {{ ref('room_controls_log') }}
{{ sink_append_pg('room_controls_log', 'zero', 'domestic') }}
