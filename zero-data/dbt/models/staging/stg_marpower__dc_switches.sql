-- The DC switches =05.71 to =05.78 of the 700 VDC ring, one table for all with the switch in technical_name.
-- Each switch measures current and voltage on both of its sections.
{% set measurements = ['dcc_s_0', 'dcc_s_1', 'dcv_s_0', 'dcv_s_1'] %}

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
from {{ source('raw', 'marpower__dc_700v__dc_switch') }}
where "topic" is not null
