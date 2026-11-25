-- The unallocated load of the 700 VDC ring per minute, classed per segment (dc_ring_segment_metadata):
-- Propulsion / Thrusters (unallocated) for SB.01.P01 and P04, Technical / 700VDC unallocated for the other
-- four. The cable segments are left out: their remainder is measurement error, not load. Kept as measured,
-- so a minute can be below zero.
-- One view for both main group and sub group panels, as each main group has one sub group.
select
    seg.time,
    meta.main_group,
    meta.sub_group,
    sum(seg.unallocated_power)  as power
from {{ ref('slv_dc_ring_segments') }} as seg
join {{ source('metadata', 'dc_ring_segment_metadata') }} as meta
    on seg.segment = meta.segment
where meta.main_group is not null
group by seg.time, meta.main_group, meta.sub_group
