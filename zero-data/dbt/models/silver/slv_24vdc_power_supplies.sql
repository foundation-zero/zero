-- Output power of each 24 VDC power supply, in W, labelled with the converter group it belongs to.
with dc_24v as (
    select
        ts,
        topic,
        power__value,
        power__has_value,
        power__is_valid
    from {{ ref('stg_marpower__24vdc') }}
),

metadata as (
    select
        topic,
        converter
    from {{ source('metadata', 'dc_24v_metadata') }}
    where converter_subnr is not null
)

select
    dc.ts,
    dc.topic,
    meta.converter,
    dc.power__value as power
from dc_24v as dc
join metadata as meta
    on dc.topic = meta.topic
where dc.power__has_value is true
and dc.power__is_valid is true
and dc.power__value is not null
