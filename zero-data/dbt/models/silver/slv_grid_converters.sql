-- Power of the two uGrid grid converters on both sides, in W: the DC input from the 700 VDC bus
-- (PvPower, published in kW) and the AC output into the 400 VAC switchboard (its incoming breaker).
-- Neither converter runs backwards (F21), so both sides are positive while it runs; the AC side reads a
-- few W below zero when the converter is idle.
select
    ts,
    topic,
    technical_name          as converter,
    'dc'                    as side,
    pv_power__value * 1000  as power
from {{ ref('stg_marpower__dc_ac_inverters') }}
where technical_name in ('05-11-u101', '05-12-u101')
and pv_power__has_value is true
and pv_power__is_valid is true
and pv_power__value is not null

UNION ALL

select
    ts,
    topic,
    case technical_name
        when '10p0-1-100q01' then '05-11-u101'
        when '10p0-3-300q01' then '05-12-u101'
    end                     as converter,
    'ac'                    as side,
    active_power__value     as power
from {{ ref('stg_marpower__ac_400v_breakers') }}
where technical_name in ('10p0-1-100q01', '10p0-3-300q01')
and active_power__has_value is true
and active_power__is_valid is true
and active_power__value is not null
