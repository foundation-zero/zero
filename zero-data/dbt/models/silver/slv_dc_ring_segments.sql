-- The load per segment of the 700 VDC ring, per minute, in W: the power that flows into a segment through
-- its DC switches and doesn't flow out (load_power), the part its measured sources take (measured_power),
-- and the rest (unallocated_power), the load no signal covers.
--
-- Summed over all segments, the switch flows cancel: the unallocated power of all segments together is the
-- gap between what the measured sources feed in and take out, whatever the switches read. The switches only
-- decide on which segment it shows. The two cable segments have nothing connected: their remainder is the
-- measurement error of the switches.
--
-- Only minutes in which all 8 switches report count. A measured source without data in a minute counts as
-- 0, so a stopped feed moves its load into the remainder of its segment, as a step.
with switch_power as (
    -- Before 20 Oct 2026 the switch currents mostly read about -1000 A, also when marked valid: a switch
    -- doesn't carry 1000 A (≈ 665 kW) here, so those samples are left out.
    select
        date_bin('1 minute'::interval, ts)  as time,
        technical_name,
        avg(
            (cast(dcc_s_0__value as double) * dcv_s_0__value
             + cast(dcc_s_1__value as double) * dcv_s_1__value) / 2
        )                                   as power
    from {{ ref('stg_marpower__dc_switches') }}
    where dcc_s_0__has_value is true
    and dcc_s_0__is_valid is true
    and dcc_s_1__has_value is true
    and dcc_s_1__is_valid is true
    and dcv_s_0__has_value is true
    and dcv_s_0__is_valid is true
    and dcv_s_1__has_value is true
    and dcv_s_1__is_valid is true
    and abs(dcc_s_0__value) < 1000
    and abs(dcc_s_1__value) < 1000
    group by time, technical_name
),

complete_minute as (
    select time
    from switch_power
    group by time
    having count(*) = 8
),

segment_flow as (
    select
        sw.time,
        meta.downstream_segment             as segment,
        meta.sign * sw.power            as power
    from switch_power as sw
    join {{ source('metadata', 'dc_ring_switch_metadata') }} as meta
        on sw.technical_name = meta.technical_name

    union all

    select
        sw.time,
        meta.upstream_segment               as segment,
        -meta.sign * sw.power           as power
    from switch_power as sw
    join {{ source('metadata', 'dc_ring_switch_metadata') }} as meta
        on sw.technical_name = meta.technical_name
),

segment_load as (
    select
        flow.time,
        flow.segment,
        sum(flow.power)                     as power
    from segment_flow as flow
    join complete_minute
        on flow.time = complete_minute.time
    group by flow.time, flow.segment
),

segment_measured as (
    select
        src.time,
        meta.segment,
        sum(src.power)                   as power
    from {{ ref('slv_dc_ring_sources') }} as src
    join {{ source('metadata', 'dc_ring_source_metadata') }} as meta
        on src.kind = meta.kind
        and src.unit = meta.unit
    group by src.time, meta.segment
)

select
    seg_load.time,
    seg_load.segment,
    seg_load.power                                  as load_power,
    coalesce(measured.power, 0)                     as measured_power,
    seg_load.power - coalesce(measured.power, 0)    as unallocated_power
from segment_load as seg_load
left join segment_measured as measured
    on seg_load.time = measured.time
    and seg_load.segment = measured.segment
