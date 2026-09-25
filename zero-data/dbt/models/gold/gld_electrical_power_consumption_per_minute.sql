{{ config(materialized='view') }}

select
    time,
    sum(avg_power) as power,
    main_group,
    sub_group
from {{ ref('gld_power_tags_active_power_per_minute') }}
where main_group is not null
group by
    time,
    main_group,
    sub_group
