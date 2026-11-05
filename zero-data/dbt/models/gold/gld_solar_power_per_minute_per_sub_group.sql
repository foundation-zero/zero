-- Power is production delivered to the DC bus (sign flipped in slv_solar_converters);
-- draw from the bus (e.g. standby) counts as zero.
select
    date_bin('1 minute'::interval, ts)              as time,
    topic,
    converter,
    'Solar'                                         as main_group,
    bimini                                          as sub_group,
    avg(case when power > 0 then power else 0 end)  as power
from {{ ref('slv_solar_converters') }}
group by time, topic, converter, bimini
