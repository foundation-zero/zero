select 
    ts,
    topic,
    consumer,
    active_power_total as power,
    main_group,
    sub_group
from {{ ref('slv_power_tags') }}
