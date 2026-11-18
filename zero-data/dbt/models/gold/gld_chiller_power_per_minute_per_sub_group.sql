-- Power of the compression chiller: the sum of its devices' averages per minute.
with device_power_per_minute as (
    select
        date_bin('1 minute'::interval, ts) as time,
        device,
        avg(power)                         as power
    from {{ ref('slv_chiller') }}
    group by time, device
)

select
    time,
    'HVAC'      as main_group,
    'Chiller'   as sub_group,
    sum(power)  as power
from device_power_per_minute
group by time
