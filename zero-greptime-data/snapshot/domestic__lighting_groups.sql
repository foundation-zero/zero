CREATE TABLE IF NOT EXISTS "domestic__lighting_groups" (
  "timestamp" TIMESTAMP(9) NOT NULL,
  "id" STRING NULL,
  "level" DOUBLE NULL,
  "room_id" STRING NULL,
  "source_type" STRING NULL,
  "table" STRING NULL,
  "topic" STRING NULL,
  TIME INDEX ("timestamp")
)

ENGINE=mito
WITH(
  append_mode = 'true',
  comment = 'Created on insertion'
)
