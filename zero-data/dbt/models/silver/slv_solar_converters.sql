-- Power each solar EPC converter delivers to the main DC bus, labelled with the bimini it serves.
with busbar as (
    select
        ts,
        topic,
        hvdc_power__value,
        hvdc_power__has_value,
        hvdc_power__is_valid
    from {{ ref('stg_marpower__busbar') }}
    where topic in (
        'marpower/busbar/epc-31-t101',
        'marpower/busbar/epc-32-t101',
        'marpower/busbar/epc-32-t102'
    )
)

select
    ts,
    topic,
    replace(topic, 'marpower/busbar/', '') as converter,
    case
        when topic = 'marpower/busbar/epc-32-t102' then 'Owners bimini'
        else 'Main bimini'
    end                                    as bimini,
    hvdc_power__value                      as power
from busbar
where hvdc_power__has_value is true
and hvdc_power__is_valid is true
and hvdc_power__value is not null
