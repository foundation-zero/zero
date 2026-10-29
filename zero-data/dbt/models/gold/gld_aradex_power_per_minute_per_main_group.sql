with per_aradex as (
    select
        date_bin('1 minute'::interval, ts) as time,
        thruster,
        aradex,
        avg(power)                         as power
    from {{ ref('slv_pcs_aradexes') }}
    group by time, thruster, aradex
)

select
    time,
    case when power >= 0 then 'Propulsion' else 'Hydrogeneration' end as main_group,
    sum(abs(power))                                                   as power
from per_aradex
group by time, main_group
