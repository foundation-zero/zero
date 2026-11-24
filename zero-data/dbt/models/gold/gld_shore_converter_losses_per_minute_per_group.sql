-- Losses / Shore converters per minute: the AC power the ESI converters draw from shore minus the DC power
-- they deliver to the 700 VDC bus, summed over the modules. A module counts only while it runs: an idle
-- module's DC reading is a sensor offset (see slv_shore_power_converters).
-- One view for both main group and sub group panels, as the sub group is a constant.
with module_loss_per_minute as (
    select
        date_bin('1 minute'::interval, ts)                          as time,
        module,
        avg(case when running then ac_power - dc_power else 0 end) as power
    from {{ ref('slv_shore_power_converters') }}
    group by time, module
)

select
    time,
    'Losses'            as main_group,
    'Shore converters'  as sub_group,
    sum(power)          as power
from module_loss_per_minute
group by time
