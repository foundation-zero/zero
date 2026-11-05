-- The solar (PV) EPC converters publish to one table per converter since 5 Nov 2026 06:07 UTC;
-- before that they published to `marpower__busbar` (see stg_marpower__busbar).
{% set tables = [
    'marpower__450000_dc_distribution__pv_converter_main_1',
    'marpower__450000_dc_distribution__pv_converter_main_2',
    'marpower__450000_dc_distribution__pv_converter_owner',
] %}
{% set measurements = ['hvdc_current', 'hvdc_power', 'hvdc_voltage', 'lvdc_current', 'lvdc_voltage'] %}

{% for table in tables %}
select
  "timestamp" as ts,
  "topic",
  {%- for measurement in measurements %}
  "{{ measurement }}__has_value",
  "{{ measurement }}__is_valid",
  "{{ measurement }}__timestamp",
  "{{ measurement }}__value"{{ "," if not loop.last }}
  {%- endfor %}
from {{ source('raw', table) }}
where "topic" is not null
{% if not loop.last %}union all{% endif %}
{% endfor %}
