select 
    date_bin('1 minute'::interval, ts) as time,
    topic,
    consumer,
    avg(active_power_total)            as power,
    main_group,
    sub_group
from {{ ref('slv_power_tags') }}
group by time, topic, consumer, main_group, sub_group
