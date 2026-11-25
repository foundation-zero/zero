-- The Termodinamica compression chiller: the power of its two compressors and its seawater pump.
-- The bridge labels the power registers "1=0,01 Watt", but the stored values are kW (see slv_chiller).
select
  "timestamp" as ts,
  "topic",
  "watt_ac_compressor_1",
  "watt_ac_compressor_2",
  "watt_sea_water_pump"
from {{ source('raw', 'termodinamica__ac_misc') }}
where "topic" is not null
