-- Positive HVDC power is assumed to be production; negative readings (standby draw) count as zero.
-- Revisit once the solar converters report real production data.
select
    date_bin('1 minute'::interval, ts)              as time,
    topic,
    converter,
    'Solar'                                         as main_group,
    bimini                                          as sub_group,
    avg(case when power > 0 then power else 0 end)  as power
from {{ ref('slv_solar_converters') }}
group by time, topic, converter, bimini
