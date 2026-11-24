-- Shore power: the AC power the ESI converters draw from shore, counted only while a module runs, as in
-- gld_shore_converter_losses_per_minute_per_group. Shore minus the converter losses is the DC power the
-- converters deliver to the 700 VDC bus.
select
    date_bin('1 minute'::interval, ts)                      as time,
    topic,
    module,
    'Shore'                                                 as main_group,
    converter                                               as sub_group,
    avg(case when running then ac_power else 0 end)        as power
from {{ ref('slv_shore_power_converters') }}
group by time, topic, module, converter
