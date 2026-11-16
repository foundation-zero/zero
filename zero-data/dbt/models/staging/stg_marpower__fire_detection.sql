-- The fire detection system publishes one table per device kind; the three share their keys.
{% set measurements = ['alarm', 'disabled', 'fault', 'pre_alarm', 'test'] %}
{% set tables = [
    'marpower__fire_detection__call_point',
    'marpower__fire_detection__detector',
    'marpower__fire_detection__sounder',
] %}

{% for table in tables %}
select
  "timestamp" as "ts",
  "topic",
  "technical_name",
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
