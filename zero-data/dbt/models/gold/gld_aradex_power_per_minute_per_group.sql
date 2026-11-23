-- Aradex power per minute, with its main group (Propulsion or Hydrogeneration) and sub group: all four
-- Aradexes (AFT and FWD thruster) are Thrusters. Unlike the power tag, 24 VDC, shore and solar sources there's
-- no separate _per_main_group view: the sub group is a constant, so a main group panel reads this view at no
-- extra cost and selects only the columns it needs.
with aradex_power_per_minute as (
    select
        date_bin('1 minute'::interval, ts)       as time,
        thruster,
        aradex,
        avg(case when power >= 0 then power else 0 end) as propulsion_power,
        avg(case when power < 0 then -power else 0 end) as hydrogeneration_power
    from {{ ref('slv_pcs_aradexes') }}
    group by time, thruster, aradex
)

select
    time,
    'Propulsion'               as main_group,
    'Thrusters'                as sub_group,
    sum(propulsion_power)      as power
from aradex_power_per_minute
group by time

union all

select
    time,
    'Hydrogeneration'          as main_group,
    'Thrusters'                as sub_group,
    sum(hydrogeneration_power) as power
from aradex_power_per_minute
group by time
