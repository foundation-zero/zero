-- Power of the compression chiller's two compressors and its seawater pump, one row per device.
-- The Termodinamica IO list and the bridge call the power registers "1=0,01 Watt", but the values
-- are kW: power / current is 239 V for all three devices, and on 26 Jun 2026 the 700 VDC segment
-- SB.01.P02 followed the chiller at 0.93 kW per kW. The source reports kW, so it is converted to W.
select
    ts,
    topic,
    'Compressor 1'                  as device,
    watt_ac_compressor_1 * 1000     as power
from {{ ref('stg_termodinamica__ac_misc') }}
where watt_ac_compressor_1 is not null

union all

select
    ts,
    topic,
    'Compressor 2'                  as device,
    watt_ac_compressor_2 * 1000     as power
from {{ ref('stg_termodinamica__ac_misc') }}
where watt_ac_compressor_2 is not null

union all

select
    ts,
    topic,
    'Seawater pump'                 as device,
    watt_sea_water_pump * 1000      as power
from {{ ref('stg_termodinamica__ac_misc') }}
where watt_sea_water_pump is not null
