with aradex_power_per_minute as (
	select
		date_bin('1 minute'::interval, ts) as time,
		thruster,
		aradex,
		case
			when power >= 0 then 'Propulsion'
			when power < 0 then 'Hydrogeneration'
		end as main_group,
		avg(abs(power)) as avg_power
	from {{ ref('slv_pcs_aradexes') }}
	group by time, topic, thruster, aradex, main_group
)

select
	time,
	main_group,
	sum(avg_power) as power
from aradex_power_per_minute
group by time, main_group
