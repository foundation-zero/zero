<script setup lang="ts">
import RoomsToggle from "@/modules/domestic/admin/components/room-tiles/RoomsToggle.vue";
import RoomTiles from "@/modules/domestic/admin/components/room-tiles/RoomTiles.vue";
import TileLights from "@/modules/domestic/admin/components/room-tiles/TileLights.vue";
</script>

<template>
  <RoomTiles>
    <template #header="{ area }">
      <RoomsToggle :rooms="area.rooms" />
    </template>
    <template #default="{ room }">
      <TileLights :room="room" />
    </template>
  </RoomTiles>
</template>
