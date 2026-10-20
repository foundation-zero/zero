select
  ts,
  topic,
  'AFT' as thruster,
  1 as aradex,
  power__value * 100 as power,
  from {{ ref('stg_marpower__pcs_aft_aradex1') }}
  where power__value is not null
  and power__has_value is true
  and power__is_valid is true

UNION ALL

select
  ts,
  topic,
  'AFT' as thruster,
  2 as aradex,
  power__value * 100 as power,
from {{ ref('stg_marpower__pcs_aft_aradex2') }}
where power__value is not null
and power__has_value is true
and power__is_valid is true

UNION ALL

select
  ts,
  topic,
  'FWD' as thruster,
  1 as aradex,
  power__value * 100 as power,
from {{ ref('stg_marpower__pcs_fwd_aradex1') }}
where power__value is not null
and power__has_value is true
and power__is_valid is true

UNION ALL

select
  ts,
  topic,
  'FWD' as thruster,
  2 as aradex,
  power__value * 100 as power,
from {{ ref('stg_marpower__pcs_fwd_aradex2') }}
where power__value is not null
and power__has_value is true
and power__is_valid is true
