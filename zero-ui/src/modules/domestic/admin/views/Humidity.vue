<script setup lang="ts">
import RoomTiles from "@/modules/domestic/admin/components/room-tiles/RoomTiles.vue";
import TileHumidity from "@/modules/domestic/admin/components/room-tiles/TileHumidity.vue";
</script>

<template>
  <RoomTiles>
    <template #default="{ room }">
      <TileHumidity :room="room" />
    </template>
  </RoomTiles>
</template>
