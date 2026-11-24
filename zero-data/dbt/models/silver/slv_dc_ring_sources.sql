-- The measured sources on the 700 VDC ring, per minute and per unit, in W: what each unit takes from the
-- bus, so a source that feeds the bus is negative. dc_ring_source_metadata places each unit on its segment.
-- Each device (module, pack, power supply, Aradex) is averaged per minute, then summed per unit.
with device_power as (
    -- Shore power converters, while a module runs (see slv_shore_power_converters).
    select
        date_bin('1 minute'::interval, ts)                      as time,
        'shore_converter'                                       as kind,
        substr(module, 1, 5)                                    as unit,
        module                                                  as device,
        avg(case when running then -dc_power else 0 end)       as power
    from {{ ref('slv_shore_power_converters') }}
    group by time, module

    union all

    -- Battery converters: the BMS battery power, positive while discharging, in kW. It is measured on the
    -- battery side, so the converter losses stay in the segment remainder.
    select
        date_bin('1 minute'::interval, ts)                      as time,
        'battery'                                               as kind,
        left(split_part(topic, '/', 4), 5)                      as unit,
        topic                                                   as device,
        avg(-battery_power * 1000)                              as power
    from {{ ref('slv_batteries') }}
    where battery_power is not null
    group by time, topic

    union all

    -- Grid converters, their DC input.
    select
        date_bin('1 minute'::interval, ts)                      as time,
        'grid_converter'                                        as kind,
        converter                                               as unit,
        converter                                               as device,
        avg(power)                                              as power
    from {{ ref('slv_grid_converters') }}
    where side = 'dc'
    group by time, converter

    union all

    -- 350 VDC converters, their 700 VDC side.
    select
        date_bin('1 minute'::interval, ts)                      as time,
        'dc_350v_converter'                                     as kind,
        converter                                               as unit,
        converter                                               as device,
        avg(power)                                              as power
    from {{ ref('slv_350vdc_converters') }}
    group by time, converter

    union all

    -- 24 VDC power supplies, their output: the input isn't measured.
    select
        date_bin('1 minute'::interval, ts)                      as time,
        'dc_24v_converter'                                      as kind,
        converter                                               as unit,
        topic                                                   as device,
        avg(power)                                              as power
    from {{ ref('slv_24vdc_power_supplies') }}
    group by time, converter, topic

    union all

    -- Thruster drives: positive for propulsion, negative for hydrogeneration.
    select
        date_bin('1 minute'::interval, ts)                      as time,
        'aradex'                                                as kind,
        concat(thruster, '-', cast(aradex as string))           as unit,
        topic                                                   as device,
        avg(power)                                              as power
    from {{ ref('slv_pcs_aradexes') }}
    group by time, thruster, aradex, topic

    union all

    -- Compression chiller: its compressors and seawater pump.
    select
        date_bin('1 minute'::interval, ts)                      as time,
        'chiller'                                               as kind,
        'chiller'                                               as unit,
        device,
        avg(power)                                              as power
    from {{ ref('slv_chiller') }}
    group by time, device
)

select
    time,
    kind,
    unit,
    sum(power) as power
from device_power
group by time, kind, unit
