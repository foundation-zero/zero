-- Power each ESI shore power converter module draws from shore, labelled with its converter.
-- Until 23 Oct 2026 09:30 UTC the modules published to topics named 70-xx, since then to 07-xx.
-- Both are combined under the same module name so the history stays continuous.
-- Once the 70-xx history is copied to the 07-xx topics, the 70-xx part can go.
with modules as (
    select
        ts,
        topic,
        case topic
            when 'marpower/450000-dc-distribution-esi/70-11-tbc1a' then '07-11-tbc1a'
            when 'marpower/450000-dc-distribution-esi/70-11-tbc1b' then '07-11-tbc1b'
            when 'marpower/450000-dc-distribution-esi/70-12-tbc1a' then '07-12-tbc1a'
            when 'marpower/450000-dc-distribution-esi/70-12-tbc1b' then '07-12-tbc1b'
        end                                         as module,
        esi_ac_bus_active_power_3_phase__value      as power_value,
        esi_ac_bus_active_power_3_phase__has_value  as power_has_value,
        esi_ac_bus_active_power_3_phase__is_valid   as power_is_valid
    from {{ ref('stg_marpower__esi') }}
    where ts < TIMESTAMP '2026-10-23 09:30:00'

    union all

    select
        ts,
        topic,
        case topic
            when 'marpower/450000-dc-distribution-esi/07-11-tbc1a' then '07-11-tbc1a'
            when 'marpower/450000-dc-distribution-esi/07-11-tbc1b' then '07-11-tbc1b'
            when 'marpower/450000-dc-distribution-esi/07-12-tbc1a' then '07-12-tbc1a'
            when 'marpower/450000-dc-distribution-esi/07-12-tbc1b' then '07-12-tbc1b'
        end                                         as module,
        esi_ac_bus_active_power_3_phase__value      as power_value,
        esi_ac_bus_active_power_3_phase__has_value  as power_has_value,
        esi_ac_bus_active_power_3_phase__is_valid   as power_is_valid
    from {{ ref('stg_marpower__esi') }}
    where ts >= TIMESTAMP '2026-10-23 09:30:00'
)

select
    ts,
    topic,
    module,
    case
        when module like '07-11-%' then 'Shore power converter PS'
        else 'Shore power converter SB'
    end                                             as converter,
    -- TODO: The ESI source reports kW; it should report W. Once the source is changed
    -- to W, remove this conversion (* 1000).
    power_value * 1000                              as power
from modules
where module is not null
and power_has_value is true
and power_is_valid is true
and power_value is not null
