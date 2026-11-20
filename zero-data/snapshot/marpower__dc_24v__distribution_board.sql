CREATE TABLE IF NOT EXISTS "marpower__dc_24v__distribution_board" (
  "timestamp" TIMESTAMP(9) NOT NULL,
  "current__has_value" BOOLEAN NULL,
  "current__is_valid" BOOLEAN NULL,
  "current__timestamp" STRING NULL,
  "current__value" DOUBLE NULL,
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
