-- Active power of each power tag, in W. The groups in power_tag_metadata are joined by the query that reads
-- this view, after it has averaged the rows per topic: joining them to every row is what made it slow.
select
    ts,
    topic,
    panel,
    consumer,
    active_power_total
from {{ ref('stg_marpower__power_tags') }}
where active_power_total is not null
