-- Power each solar EPC converter delivers to the main DC bus, labelled with the bimini it serves.
-- Until 5 Nov 2026 06:07 UTC the converters published to the busbar table, since then to one table
-- per converter. Both sources are combined under the same converter name so the history stays continuous.
-- Once the busbar history is copied into the new tables, the busbar part can go.
with busbar as (
    select
        ts,
        topic,
        replace(topic, 'marpower/busbar/', '') as converter,
        hvdc_power__value,
        hvdc_power__has_value,
        hvdc_power__is_valid
    from {{ ref('stg_marpower__busbar') }}
    where topic in (
        'marpower/busbar/epc-31-t101',
        'marpower/busbar/epc-32-t101',
        'marpower/busbar/epc-32-t102'
    )
),

pv_converters as (
    select
        ts,
        topic,
        case topic
            when 'marpower/450000-dc-distribution/pv-converter-main-1' then 'epc-31-t101'
            when 'marpower/450000-dc-distribution/pv-converter-main-2' then 'epc-32-t101'
            when 'marpower/450000-dc-distribution/pv-converter-owner' then 'epc-32-t102'
        end                                    as converter,
        hvdc_power__value,
        hvdc_power__has_value,
        hvdc_power__is_valid
    from {{ ref('stg_marpower__pv_converters') }}
),

converters as (
    select * from busbar
    union all
    select * from pv_converters
)

select
    ts,
    topic,
    converter,
    case
        when converter = 'epc-32-t102' then 'Owners bimini'
        else 'Main bimini'
    end                                    as bimini,
    hvdc_power__value                      as power
from converters
where converter is not null
and hvdc_power__has_value is true
and hvdc_power__is_valid is true
and hvdc_power__value is not null
