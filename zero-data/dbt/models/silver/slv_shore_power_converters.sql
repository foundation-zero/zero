-- Power each ESI shore power converter module draws from shore, labelled with its converter.
select
    ts,
    topic,
    technical_name                                   as module,
    case
        when technical_name like '07-11-%' then 'Shore power converter PS'
        else 'Shore power converter SB'
    end                                              as converter,
    -- TODO: The ESI source reports kW; it should report W. Once the source is changed
    -- to W, remove this conversion (* 1000).
    esi_ac_bus_active_power_3_phase__value * 1000    as power
from {{ ref('stg_marpower__esi') }}
where esi_ac_bus_active_power_3_phase__has_value is true
and esi_ac_bus_active_power_3_phase__is_valid is true
and esi_ac_bus_active_power_3_phase__value is not null
