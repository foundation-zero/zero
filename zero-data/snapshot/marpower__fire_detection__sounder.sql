CREATE TABLE IF NOT EXISTS "marpower__fire_detection__sounder" (
  "timestamp" TIMESTAMP(9) NOT NULL,
  "alarm__has_value" BOOLEAN NULL,
  "alarm__is_valid" BOOLEAN NULL,
  "alarm__timestamp" STRING NULL,
  "alarm__value" BOOLEAN NULL,
  "disabled__has_value" BOOLEAN NULL,
  "disabled__is_valid" BOOLEAN NULL,
  "disabled__timestamp" STRING NULL,
  "disabled__value" BOOLEAN NULL,
  "fault__has_value" BOOLEAN NULL,
  "fault__is_valid" BOOLEAN NULL,
  "fault__timestamp" STRING NULL,
  "fault__value" BOOLEAN NULL,
  "pre_alarm__has_value" BOOLEAN NULL,
  "pre_alarm__is_valid" BOOLEAN NULL,
  "pre_alarm__timestamp" STRING NULL,
  "pre_alarm__value" BOOLEAN NULL,
  "technical_name" STRING NULL,
  "test__has_value" BOOLEAN NULL,
  "test__is_valid" BOOLEAN NULL,
  "test__timestamp" STRING NULL,
  "test__value" BOOLEAN NULL,
  "topic" STRING NULL,
  TIME INDEX ("timestamp")
)

ENGINE=mito
WITH(
  'comment' = 'Created on insertion',
  append_mode = 'true'
)
