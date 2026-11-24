-- Power each solar EPC converter delivers to the main DC bus, labelled with the bimini it serves.
with converters as (
    select
        ts,
        topic,
        case technical_name
            when '04-31-t101' then 'epc-31-t101'
            when '04-32-t101' then 'epc-32-t101'
            when '04-32-t102' then 'epc-32-t102'
        end                                    as converter,
        hvdc_power__value,
        hvdc_power__has_value,
        hvdc_power__is_valid
    from {{ ref('stg_marpower__pv_converters') }}
)

select
    ts,
    topic,
    converter,
    case
        -- System 04.31 is on the owners bimini, 04.32 on the main bimini.
        when converter = 'epc-31-t101' then 'Owners bimini'
        else 'Main bimini'
    end                                    as bimini,
    -- Marpower reports HVDC power negative when it flows from the panels to the DC bus;
    -- flip it so power is the production delivered to the bus (positive).
    -hvdc_power__value                     as power
from converters
where converter is not null
and hvdc_power__has_value is true
and hvdc_power__is_valid is true
and hvdc_power__value is not null
