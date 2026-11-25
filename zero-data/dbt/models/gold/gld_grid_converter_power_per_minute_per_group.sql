-- The AC side of the energy balance, per minute, with two rows per minute:
-- - Technical / AC unallocated: the grid converters' AC output minus the power tag total, the AC load
--   without a power tag. Minutes without power tag data count the whole AC output as unallocated.
-- - Losses / Grid converters: DC input minus AC output, per converter in the minutes where both sides
--   have data. Kept as measured: an idle converter gives a few W below zero.
-- One view for both main group and sub group panels, as each sub group is a constant.
with converter_power_per_minute as (
    select
        date_bin('1 minute'::interval, ts)              as time,
        converter,
        avg(case when side = 'dc' then power end)       as dc_power,
        avg(case when side = 'ac' then power end)       as ac_power
    from {{ ref('slv_grid_converters') }}
    group by time, converter
),

converter_total as (
    select
        time,
        sum(ac_power)            as ac_power,
        sum(dc_power - ac_power) as loss_power
    from converter_power_per_minute
    group by time
),

power_tag_total as (
    select
        time,
        sum(power) as power
    from {{ ref('gld_power_tags_power_per_minute_per_main_group') }}
    group by time
)

select
    converter.time,
    'Technical'                                        as main_group,
    'AC unallocated'                                   as sub_group,
    converter.ac_power - coalesce(power_tag.power, 0)  as power
from converter_total as converter
left join power_tag_total as power_tag
    on power_tag.time = converter.time
where converter.ac_power is not null

union all

select
    time,
    'Losses'                                           as main_group,
    'Grid converters'                                  as sub_group,
    loss_power                                         as power
from converter_total
where loss_power is not null
