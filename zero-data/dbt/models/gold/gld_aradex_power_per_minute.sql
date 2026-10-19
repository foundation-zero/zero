with aradex_powers as (
	select
		date_bin('1 minute'::interval, ts) as time,
		thruster,
		aradex,
		avg(case when power > 0 then power else 0 end) as avg_propulsion_power,
		avg(case when power < 0 then -power else 0 end) as avg_hydrogeneration_power
	from {{ ref('slv_pcs_aradexes') }}
	group by time, thruster, aradex
)

select
	time,
	sum(avg_propulsion_power) as propulsion_power,
	sum(avg_hydrogeneration_power) as hydrogeneration_power
from aradex_powers
group by time
