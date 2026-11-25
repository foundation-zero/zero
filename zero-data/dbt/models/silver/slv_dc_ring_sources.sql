-- The measured sources on the 700 VDC ring, one row per sample, in W: what each device takes from the bus, so a
-- source that feeds the bus is negative. The unit is what dc_ring_source_metadata places on a segment. The
-- 24 VDC power supplies aren't here: their unit, the converter, is in dc_24v_metadata, so the query that reads
-- this view takes them from slv_24vdc_power_supplies.

-- Shore power converters, while a module runs (see slv_shore_power_converters).
select
    ts,
    'shore_converter'                               as kind,
    substr(module, 1, 5)                            as unit,
    module                                          as device,
    case when running then -dc_power else 0 end     as power
from {{ ref('slv_shore_power_converters') }}

union all

-- Battery converters: the BMS battery power, positive while discharging, in kW. It is measured on the battery
-- side, so the converter losses stay in the segment remainder.
select
    ts,
    'battery'                                       as kind,
    left(split_part(topic, '/', 4), 5)              as unit,
    topic                                           as device,
    -battery_power * 1000                           as power
from {{ ref('slv_batteries') }}
where battery_power is not null

union all

-- Grid converters, their DC input.
select
    ts,
    'grid_converter'                                as kind,
    converter                                       as unit,
    converter                                       as device,
    power
from {{ ref('slv_grid_converters') }}
where side = 'dc'

union all

-- 350 VDC converters, their 700 VDC side.
select
    ts,
    'dc_350v_converter'                             as kind,
    converter                                       as unit,
    converter                                       as device,
    power
from {{ ref('slv_350vdc_converters') }}

union all

-- Thruster drives: positive for propulsion, negative for hydrogeneration.
select
    ts,
    'aradex'                                        as kind,
    concat(thruster, '-', cast(aradex as string))   as unit,
    topic                                           as device,
    power
from {{ ref('slv_pcs_aradexes') }}

union all

-- Compression chiller: its compressors and seawater pump.
select
    ts,
    'chiller'                                       as kind,
    'chiller'                                       as unit,
    device,
    power
from {{ ref('slv_chiller') }}
