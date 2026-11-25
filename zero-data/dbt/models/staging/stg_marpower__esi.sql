-- The ESI shore power converters, PS (07-11) and SB (07-12), each run two modules (tbc1a and tbc1b).
select
  "timestamp" as ts,
  "topic",
  "technical_name",
  "esi_ac_bus_active_power_3_phase__has_value",
  "esi_ac_bus_active_power_3_phase__is_valid",
  "esi_ac_bus_active_power_3_phase__timestamp",
  "esi_ac_bus_active_power_3_phase__value",
  "esi_battery_current__has_value",
  "esi_battery_current__is_valid",
  "esi_battery_current__timestamp",
  "esi_battery_current__value",
  "esi_battery_voltage__has_value",
  "esi_battery_voltage__is_valid",
  "esi_battery_voltage__timestamp",
  "esi_battery_voltage__value",
  "running__has_value",
  "running__is_valid",
  "running__timestamp",
  "running__value"
from {{ source('raw', 'marpower__dc_700v__shore_converter') }}
where "topic" is not null
