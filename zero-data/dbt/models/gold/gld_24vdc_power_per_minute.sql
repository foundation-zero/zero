with currents as (
	select
		date_bin('1 minute'::interval, ts) as time,
		topic,
		converter,
		AVG(output_current) as current,
		main_group,
		sub_group	
	from {{ ref('slv_24vdc_currents') }}
	group by time, topic, converter, main_group, sub_group
)
select
	cur.time,
	cur.topic,
	cur.converter,
	cur.main_group,
	cur.sub_group,
	cur.current,
	volt.voltage,
	(cur.current * volt.voltage) / 1000.0 as power
from currents as cur
join {{ ref('gld_24vdc_converter_voltage_per_minute') }} as volt
	on volt.converter = cur.converter and volt.time = cur.time
