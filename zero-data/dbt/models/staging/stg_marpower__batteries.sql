select
  "timestamp" as ts,
  "state_of_charge__value" as soc,
  "state_of_health__value" as soh,
  "number_of_connected_strings__value" as num_connected_strings,
  "energy__value" as energy,
  "charging__value" as charging,
  "dis_charging__value" as discharging,
  "charge_power__value" as charge_power,
  "battery_power__value" as battery_power,
  "table",
  "topic"
from {{ source('raw', 'marpower__450000_main_power_storage_errors') }}
