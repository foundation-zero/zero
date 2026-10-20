with dc_24v as (
    select * from {{ ref('stg_marpower__24vdc') }}
),

metadata as (
    select * from {{ source('metadata', 'dc_24v_metadata') }}
)

select
    dc.ts,
    dc.topic,
    dc.output_current__value as output_current,
    meta.converter,
    meta.main_group,
    meta.sub_group
from dc_24v as dc
join metadata as meta
    on dc.topic = meta.topic
where dc.output_current__value is not null
and dc.output_current__has_value is true
and dc.output_current__is_valid is true
and meta.main_group is not null
