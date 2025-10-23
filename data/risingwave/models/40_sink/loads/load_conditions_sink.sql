CREATE SINK {{ this }} FROM {{ ref('load_conditions') }}
{{ sink_append_pg('conditions', 'zero', 'public') }}
