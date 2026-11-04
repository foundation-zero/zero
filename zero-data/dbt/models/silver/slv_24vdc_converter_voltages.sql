with dc_24v as (
    select
        ts,
        topic,
        voltage__value,
        voltage__has_value,
        voltage__is_valid
    from {{ ref('stg_marpower__24vdc') }}
),

metadata as (
    select
        topic,
        converter,
        converter_subnr
    from {{ source('metadata', 'dc_24v_metadata') }}
)

select
    dc.ts,
    dc.topic,
    dc.voltage__value as voltage,
    meta.converter,
    meta.converter_subnr
from dc_24v as dc
join metadata as meta
    on dc.topic = meta.topic
where dc.voltage__has_value is true
and dc.voltage__is_valid is true
and dc.voltage__value > 18
and meta.converter is not null
and meta.converter_subnr is not null
