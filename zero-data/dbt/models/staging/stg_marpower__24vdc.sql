-- The 24 V system publishes one table per kind: breaker channels, power supplies and boards.
{% set value_types = {
    'active': 'BOOLEAN',
    'csetting': 'BIGINT',
    'current': 'DOUBLE',
    'device_temp': 'DOUBLE',
    'external_off': 'BOOLEAN',
    'heatsink_temp': 'DOUBLE',
    'hmi_cmd_close': 'BOOLEAN',
    'hmi_cmd_open': 'BOOLEAN',
    'isetting': 'BIGINT',
    'iwarning': 'BOOLEAN',
    'output_current': 'BIGINT',
    'power': 'DOUBLE',
    'short_circuit': 'BOOLEAN',
    'status_hmi_green': 'BOOLEAN',
    'status_hmi_red': 'BOOLEAN',
    'status_hmi_yellow': 'BOOLEAN',
    'status_on_off': 'BOOLEAN',
    'system_error': 'BOOLEAN',
    'under_voltage': 'BOOLEAN',
    'voltage': 'DOUBLE',
} %}
{% set tables = {
    'marpower__dc_24v__breaker': [
        'csetting', 'external_off', 'hmi_cmd_close', 'hmi_cmd_open', 'isetting', 'iwarning',
        'output_current', 'short_circuit', 'status_hmi_green', 'status_hmi_red',
        'status_hmi_yellow', 'status_on_off', 'system_error', 'under_voltage',
    ],
    'marpower__dc_24v__power_supply': [
        'active', 'current', 'device_temp', 'heatsink_temp', 'power', 'voltage',
    ],
    'marpower__dc_24v__distribution_board': ['current', 'power', 'voltage'],
} %}

{% for table, measurements in tables.items() %}
select
  "timestamp" as "ts",
  "topic",
  "technical_name",
  {%- for measurement, value_type in value_types.items() %}
  {%- if measurement in measurements %}
  "{{ measurement }}__has_value",
  "{{ measurement }}__is_valid",
  "{{ measurement }}__timestamp",
  "{{ measurement }}__value"{{ "," if not loop.last }}
  {%- else %}
  cast(null as BOOLEAN) as "{{ measurement }}__has_value",
  cast(null as BOOLEAN) as "{{ measurement }}__is_valid",
  cast(null as STRING) as "{{ measurement }}__timestamp",
  cast(null as {{ value_type }}) as "{{ measurement }}__value"{{ "," if not loop.last }}
  {%- endif %}
  {%- endfor %}
from {{ source('raw', table) }}
where "topic" is not null
{% if not loop.last %}union all{% endif %}
{% endfor %}
