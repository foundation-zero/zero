-- The 400 VAC switchboard's incoming breakers from the grid converters (10P0-1 Q01 from =05.11-U101,
-- 10P0-3 Q01 from =05.12-U101), one table for both with the breaker in technical_name.
{% set measurements = ['active_power'] %}

select
  "timestamp" as ts,
  "topic",
  "technical_name",
  {%- for measurement in measurements %}
  "{{ measurement }}__has_value",
  "{{ measurement }}__is_valid",
  "{{ measurement }}__timestamp",
  "{{ measurement }}__value"{{ "," if not loop.last }}
  {%- endfor %}
from {{ source('raw', 'marpower__ac_400v__breaker') }}
where "topic" is not null
