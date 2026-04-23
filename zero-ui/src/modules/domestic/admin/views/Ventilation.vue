<script setup lang="ts">
import RoomTiles from "@/modules/domestic/admin/components/room-tiles/RoomTiles.vue";
import TileCO2 from "@/modules/domestic/admin/components/room-tiles/TileCO2.vue";
</script>

<template>
  <RoomTiles>
    <template #default="{ room }">
      <TileCO2 :room="room" />
    </template>
  </RoomTiles>
</template>
