{{ config(materialized='view') }}

select 
    date_bin(INTERVAL '1 minute', ts) as time,
    topic,
    consumer,
    avg(active_power_total) as avg_power,
    main_group,
    sub_group
from {{ ref('slv_power_tags') }}
group by 
    time,
    topic,
    consumer,
    main_group,
    sub_group
