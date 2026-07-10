<script setup lang="ts">
import RoomTiles from "@/modules/domestic/admin/components/room-tiles/RoomTiles.vue";
import TileTemperature from "@/modules/domestic/admin/components/room-tiles/TileTemperature.vue";
import { computed } from "vue";
import { useHistoryStore } from "../../stores/history";

const history = useHistoryStore();

const temperaturesByRoom = computed(() => {
  return Object.fromEntries(
    (history.airConditioningLog?.rooms ?? []).map((room) => [room.id, room.airConditioningLog]),
  );
});
</script>

<template>
  <RoomTiles>
    <template #default="{ room }">
      <TileTemperature
        :room="room"
        :temperature-log="temperaturesByRoom[room.id]"
      />
    </template>
  </RoomTiles>
</template>
