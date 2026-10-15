with dc_24v as (
    select * from {{ ref('stg_marpower__24vdc') }}
),

metadata as (
    select * from {{ source('metadata', 'dc_24v_metadata') }}
)

select
    dc.ts,
    dc.topic,
    meta.converter,
    meta.converter_subnr,
    dc.voltage__value as voltage
from dc_24v as dc
join metadata as meta
    on dc.topic = meta.topic
where dc.voltage__value is not null
and meta.converter is not null
and meta.converter_subnr is not null
