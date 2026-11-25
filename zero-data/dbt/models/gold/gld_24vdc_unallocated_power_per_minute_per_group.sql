-- 24 VDC load that isn't behind a monitored breaker: the output of all 24 VDC power supplies minus the
-- breaker-level total, per minute, as Technical / 24VDC unallocated. One view for both main group and
-- sub group panels, as its sub group is a constant. Minutes without breaker data count the whole output
-- as unallocated.
with supply_power_per_minute as (
    select
        date_bin('1 minute'::interval, ts) as time,
        topic,
        avg(power)                         as power
    from {{ ref('slv_24vdc_power_supplies') }}
    group by time, topic
),

supply_total as (
    select
        time,
        sum(power) as power
    from supply_power_per_minute
    group by time
),

breaker_total as (
    select
        time,
        sum(power) as power
    from {{ ref('gld_24vdc_power_per_minute_per_main_group') }}
    group by time
)

select
    supply.time,
    'Technical'                                    as main_group,
    '24VDC unallocated'                            as sub_group,
    supply.power - coalesce(breaker.power, 0)      as power
from supply_total as supply
left join breaker_total as breaker
    on breaker.time = supply.time
