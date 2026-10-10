select
    date_bin(INTERVAL '1 minute', ts) as time,
    topic,
    AVG(soc) AS avg_soc,
    AVG(soh) AS avg_soh,
    AVG(energy) AS avg_energy,
    AVG(battery_power) AS avg_battery_power,
    AVG(charge_power) AS avg_charge_power,
    MAX(charging) AS is_charging,
    MAX(discharging) AS is_discharging
from {{ ref('slv_batteries') }}
where num_connected_strings > 0
group by
    time,
    topic
