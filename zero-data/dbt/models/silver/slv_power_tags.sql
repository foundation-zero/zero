{{ config(materialized='view') }}

with power_tags as (
    select * from {{ ref('stg_marpower__power_tags') }}
),

metadata as (
    select * from {{ ref('stg_power_tag_metadata') }}
)

select
    pt.*,
    meta.main_group,
    meta.sub_group
from power_tags as pt
left join metadata as meta
    on pt.topic = meta.topic
