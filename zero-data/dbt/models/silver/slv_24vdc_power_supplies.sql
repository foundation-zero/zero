-- Output power of each 24 VDC power supply, in W. Its converter in dc_24v_metadata is joined by the query that
-- reads this view, after it has averaged the rows per topic.
select
    ts,
    topic,
    power__value as power
from {{ ref('stg_marpower__24vdc') }}
where power__has_value is true
and power__is_valid is true
and power__value is not null
