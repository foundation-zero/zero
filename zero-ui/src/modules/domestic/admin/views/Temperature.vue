<script setup lang="ts">
import RoomTiles from "@/modules/domestic/admin/components/room-tiles/RoomTiles.vue";
import TileTemperature from "@/modules/domestic/admin/components/room-tiles/TileTemperature.vue";
</script>

<template>
  <RoomTiles>
    <template #default="{ room }">
      <TileTemperature :room="room" />
    </template>
  </RoomTiles>
</template>
