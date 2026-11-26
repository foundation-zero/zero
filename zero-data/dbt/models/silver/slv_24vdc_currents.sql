-- Output current of each 24 VDC breaker channel. Its converter and groups in dc_24v_metadata are joined by the
-- query that reads this view, after it has averaged the rows per topic.
select
    ts,
    topic,
    output_current__value as output_current
from {{ ref('stg_marpower__24vdc') }}
where output_current__has_value is true
and output_current__is_valid is true
and output_current__value is not null
