-- Power through each DC switch of the 700 VDC ring (05.71–05.78), in W: current × voltage, averaged over the
-- switch's two sections. Positive in the direction of section 0 to section 1; dc_ring_switch_metadata gives the
-- sign that turns it into a flow from the upstream to the downstream segment.
--
-- Before 20 Oct 2026 the switch currents mostly read about -1000 A, also when marked valid: a switch doesn't
-- carry 1000 A (≈ 665 kW) here, so those samples are left out.
select
    ts,
    topic,
    technical_name,
    (cast(dcc_s_0__value as double) * dcv_s_0__value
     + cast(dcc_s_1__value as double) * dcv_s_1__value) / 2 as power
from {{ ref('stg_marpower__dc_switches') }}
where dcc_s_0__has_value is true
and dcc_s_0__is_valid is true
and dcc_s_0__value is not null
and dcc_s_1__has_value is true
and dcc_s_1__is_valid is true
and dcc_s_1__value is not null
and dcv_s_0__has_value is true
and dcv_s_0__is_valid is true
and dcv_s_0__value is not null
and dcv_s_1__has_value is true
and dcv_s_1__is_valid is true
and dcv_s_1__value is not null
and abs(dcc_s_0__value) < 1000
and abs(dcc_s_1__value) < 1000
