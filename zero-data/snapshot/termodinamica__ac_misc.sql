CREATE TABLE IF NOT EXISTS "termodinamica__ac_misc" (
  "timestamp" TIMESTAMP(9) NOT NULL,
  "ac_compressor_1" DOUBLE NULL,
  "ac_compressor_2" DOUBLE NULL,
  "current_req_pressure" DOUBLE NULL,
  "engine_box_compressor_2_speed" DOUBLE NULL,
  "engine_box_compressor_speed" DOUBLE NULL,
  "engine_box_p_condenser" DOUBLE NULL,
  "engine_box_p_gas" DOUBLE NULL,
  "engine_box_p_liquid" DOUBLE NULL,
  "engine_box_t_sea_water" DOUBLE NULL,
  "engine_box_water_pump_speed" DOUBLE NULL,
  "sea_water_pump" DOUBLE NULL,
  "source_type" STRING NULL,
  "table" STRING NULL,
  "topic" STRING NULL,
  "watt_ac_compressor_1" DOUBLE NULL,
  "watt_ac_compressor_2" DOUBLE NULL,
  "watt_sea_water_pump" DOUBLE NULL,
  TIME INDEX ("timestamp")
)

ENGINE=mito
WITH(
  append_mode = 'true',
  comment = 'Created on insertion'
)
