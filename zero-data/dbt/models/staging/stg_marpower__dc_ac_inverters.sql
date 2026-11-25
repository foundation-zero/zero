-- The two uGrid grid converters (Aradex DC/AC inverters =05.11-U101 aft, =05.12-U101 fwd) between the
-- 700 VDC bus and the 400 VAC switchboard, one table for both with the converter in technical_name.
{% set measurements = ['pv_current', 'pv_power'] %}

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
from {{ source('raw', 'marpower__dc_ac__inverter') }}
where "topic" is not null
