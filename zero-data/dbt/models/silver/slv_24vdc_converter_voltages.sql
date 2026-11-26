-- Output voltage of each 24 VDC power supply, in V; a reading of 18 V or less isn't a valid output voltage. Its
-- converter and converter_subnr in dc_24v_metadata are joined by the query that reads this view, after it has
-- averaged the rows per topic.
select
    ts,
    topic,
    voltage__value as voltage
from {{ ref('stg_marpower__24vdc') }}
where voltage__has_value is true
and voltage__is_valid is true
and voltage__value > 18
