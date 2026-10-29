select
    date_bin('1 minute'::interval, ts) as time,
    topic,
    AVG(soc)                           as avg_soc,
    AVG(soh)                           as avg_soh,
    AVG(energy)                        as avg_energy,
    AVG(battery_power)                 as avg_battery_power,
    AVG(charge_power)                  as avg_charge_power,
    MAX(charging)                      as is_charging,
    MAX(discharging)                   as is_discharging
from {{ ref('slv_batteries') }}
where num_connected_strings > 0
group by time, topic
