-- Power each 350 VDC converter draws from the 700 VDC bus, in W. Positive is from the 700 VDC bus to
-- the 350 VDC network. A converter can also run the other way (02-71-t102 often does): the 350 VDC
-- network is tied between aft and fwd, so power can flow in at one converter and back out at another.
-- Only the sum over the four converters is the load of the 350 VDC network.
select
    ts,
    topic,
    technical_name      as converter,
    hvdc_power__value   as power
from {{ ref('stg_marpower__dc_350v_converters') }}
where technical_name is not null
and hvdc_power__has_value is true
and hvdc_power__is_valid is true
and hvdc_power__value is not null
