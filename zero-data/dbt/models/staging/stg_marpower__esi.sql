-- The ESI shore power converters, PS (07-11) and SB (07-12), each run two modules (tbc1a and tbc1b).
-- On 23 Oct 2026 Zero renamed their topics from 70-xx to 07-xx (see slv_shore_power_converters).
select
  "timestamp" as ts,
  "topic",
  "esi_ac_bus_active_power_3_phase__has_value",
  "esi_ac_bus_active_power_3_phase__is_valid",
  "esi_ac_bus_active_power_3_phase__timestamp",
  "esi_ac_bus_active_power_3_phase__value"
from {{ source('raw', 'marpower__450000_dc_distribution_esi') }}
where "topic" is not null
