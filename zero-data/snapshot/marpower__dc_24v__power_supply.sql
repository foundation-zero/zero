CREATE TABLE IF NOT EXISTS "marpower__dc_24v__power_supply" (
  "timestamp" TIMESTAMP(9) NOT NULL,
  "active__has_value" BOOLEAN NULL,
  "active__is_valid" BOOLEAN NULL,
  "active__timestamp" STRING NULL,
  "active__value" BOOLEAN NULL,
  "current__has_value" BOOLEAN NULL,
  "current__is_valid" BOOLEAN NULL,
  "current__timestamp" STRING NULL,
  "current__value" DOUBLE NULL,
  "device_temp__has_value" BOOLEAN NULL,
  "device_temp__is_valid" BOOLEAN NULL,
  "device_temp__timestamp" STRING NULL,
  "device_temp__value" DOUBLE NULL,
  "heatsink_temp__has_value" BOOLEAN NULL,
  "heatsink_temp__is_valid" BOOLEAN NULL,
  "heatsink_temp__timestamp" STRING NULL,
  "heatsink_temp__value" DOUBLE NULL,
  "power__has_value" BOOLEAN NULL,
  "power__is_valid" BOOLEAN NULL,
  "power__timestamp" STRING NULL,
  "power__value" DOUBLE NULL,
  "technical_name" STRING NULL,
  "topic" STRING NULL,
  "voltage__has_value" BOOLEAN NULL,
  "voltage__is_valid" BOOLEAN NULL,
  "voltage__timestamp" STRING NULL,
  "voltage__value" DOUBLE NULL,
  TIME INDEX ("timestamp")
)

ENGINE=mito
WITH(
  append_mode = 'true',
  comment = 'Created on insertion'
)
