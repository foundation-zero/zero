select
  ts,
  topic,
  "state_of_charge__value" as soc,
  "state_of_health__value" as soh,
  "number_of_connected_strings__value" as num_connected_strings,
  "energy__value" as energy,
  "charging__value" as charging,
  "dis_charging__value" as discharging,
  "charge_power__value" as charge_power,
  "battery_power__value" as battery_power,
from {{ ref('stg_marpower__batteries') }}
