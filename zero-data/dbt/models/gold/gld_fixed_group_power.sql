-- Power of every device whose main group and sub group are fixed, one row per sample, in W, as the energy
-- dashboards count it. A query averages the rows per device and time bucket, then sums them per group. The
-- series that combine several signals (power tags, 24 VDC, AC unallocated, grid converter losses, the 700 VDC
-- ring remainders) are made by the dashboard queries from the silver views.

-- Shore: the AC power each ESI module draws from shore, only while it runs (see slv_shore_power_converters).
select
    ts,
    module                                              as device,
    'Shore'                                             as main_group,
    converter                                           as sub_group,
    case when running then ac_power else 0 end          as power
from {{ ref('slv_shore_power_converters') }}

union all

-- Shore converter losses: AC drawn minus DC delivered to the 700 VDC bus, only while the module runs.
select
    ts,
    module                                              as device,
    'Losses'                                            as main_group,
    'Shore converters'                                  as sub_group,
    case when running then ac_power - dc_power else 0 end as power
from {{ ref('slv_shore_power_converters') }}

union all

-- Solar: production delivered to the bus; draw from the bus (e.g. standby) counts as zero.
select
    ts,
    converter                                           as device,
    'Solar'                                             as main_group,
    bimini                                              as sub_group,
    case when power > 0 then power else 0 end           as power
from {{ ref('slv_solar_converters') }}

union all

-- Thrusters: an Aradex's positive power is propulsion, its negative power hydrogeneration. Each sample gives
-- a row for both, one of them 0, so the average per bucket is the same as splitting the average.
select
    ts,
    topic                                               as device,
    'Propulsion'                                        as main_group,
    'Thrusters'                                         as sub_group,
    case when power >= 0 then power else 0 end          as power
from {{ ref('slv_pcs_aradexes') }}

union all

select
    ts,
    topic                                               as device,
    'Hydrogeneration'                                   as main_group,
    'Thrusters'                                         as sub_group,
    case when power < 0 then -power else 0 end          as power
from {{ ref('slv_pcs_aradexes') }}

union all

-- Compression chiller: its two compressors and its seawater pump.
select
    ts,
    device,
    'HVAC'                                              as main_group,
    'Chiller'                                           as sub_group,
    power
from {{ ref('slv_chiller') }}

union all

-- 350 VDC network: the four converters' 700 VDC side. Only their sum is the load: a converter can run
-- backwards. The DcOpp outputs read 0, so the load can't be split further; the converter losses are in it.
select
    ts,
    converter                                           as device,
    'Domestic'                                          as main_group,
    'Lighting'                                          as sub_group,
    power
from {{ ref('slv_350vdc_converters') }}
