-- The four Epic Power DC/DC converters between the 700 VDC bus (high side, hvdc) and the 350 VDC
-- network (low side, lvdc), one table for all four with the converter in technical_name.
{% set measurements = ['hvdc_current', 'hvdc_power', 'hvdc_voltage', 'lvdc_current', 'lvdc_voltage'] %}

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
from {{ source('raw', 'marpower__dc_350v__dc_dc_converter') }}
where "topic" is not null
