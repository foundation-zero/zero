-- Load of the 350 VDC network: the sum of the four converters' averages per minute, as Domestic / Lighting.
-- Like the chiller, it has one view for both main group and sub group panels, as its sub group is a constant.
-- The DcOpp outputs (marpower__dc_350v__breaker) read 0 since October, so the load can't be split
-- further, and the converter losses are part of this load.
with converter_power_per_minute as (
    select
        date_bin('1 minute'::interval, ts) as time,
        converter,
        avg(power)                         as power
    from {{ ref('slv_350vdc_converters') }}
    group by time, converter
)

select
    time,
    'Domestic'  as main_group,
    'Lighting'  as sub_group,
    sum(power)  as power
from converter_power_per_minute
group by time
