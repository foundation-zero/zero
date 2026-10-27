with power_tags as (
    select 
        ts,
        topic,
        consumer,
        active_power_total
    from {{ ref('stg_marpower__power_tags') }}
),

metadata as (
    select
        topic,
        main_group,
        sub_group
    from {{ source('metadata', 'power_tag_metadata') }}
)

select
    pt.ts,
    pt.topic,
    pt.consumer,
    pt.active_power_total,
    meta.main_group,
    meta.sub_group
from power_tags as pt
left join metadata as meta
    on pt.topic = meta.topic
where pt.active_power_total is not null
and meta.main_group is not null
