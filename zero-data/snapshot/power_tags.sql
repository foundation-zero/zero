CREATE TABLE IF NOT EXISTS "power_tags" (
  "timestamp" TIMESTAMP(9) NOT NULL,
  "active_power_total" DOUBLE NULL,
  "component" STRING NULL,
  "consumer" STRING NULL,
  "current_a" DOUBLE NULL,
  "current_b" DOUBLE NULL,
  "current_c" DOUBLE NULL,
  "panel" STRING NULL,
  "power_factor_total" DOUBLE NULL,
  "source_type" STRING NULL,
  "table" STRING NULL,
  "topic" STRING NULL,
  "active_power_a" DOUBLE NULL,
  "voltage_an" DOUBLE NULL,
  "active_power_b" DOUBLE NULL,
  "active_power_c" DOUBLE NULL,
  "voltage_bn" DOUBLE NULL,
  "voltage_cn" DOUBLE NULL,
  TIME INDEX ("timestamp")
)

ENGINE=mito
WITH(
  'comment' = 'Created on insertion',
  append_mode = 'true'
)
