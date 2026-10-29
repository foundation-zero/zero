with converter_voltages as (
    select
        date_bin('1 minute'::interval, ts)                  as time,
        converter,
        avg(case when converter_subnr = 1 then voltage end) as voltage1,
        avg(case when converter_subnr = 2 then voltage end) as voltage2,
        avg(case when converter_subnr = 3 then voltage end) as voltage3
    from {{ ref('slv_24vdc_converter_voltages') }}
    group by
        time, converter
)
select
	time,
	converter,
	coalesce(voltage1, voltage2, voltage3, 24.0) as voltage
from converter_voltages
order by time, converter
