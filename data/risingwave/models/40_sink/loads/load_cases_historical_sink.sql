CREATE SINK {{ this }} AS (
  SELECT
    "sea_state",
    "awa",
    "aws",
    "pcs_mode_aft",
    "pcs_mode_fwd",
    "sails",
    "time"
  FROM
    {{ ref('load_cases_historical') }}
)
{{ sink_append_pg('load_cases_historical', 'zero') }}

