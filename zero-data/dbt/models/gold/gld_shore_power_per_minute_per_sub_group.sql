-- Power is drawn from shore (AC active power of the ESI converters);
-- a negative reading counts as zero.
select
    date_bin('1 minute'::interval, ts)              as time,
    topic,
    module,
    'Shore'                                         as main_group,
    converter                                       as sub_group,
    avg(case when power > 0 then power else 0 end)  as power
from {{ ref('slv_shore_power_converters') }}
group by time, topic, module, converter
