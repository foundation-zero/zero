<script setup lang="ts">
import RoomTiles from "@/modules/domestic/admin/components/room-tiles/RoomTiles.vue";
import TileHumidity from "@/modules/domestic/admin/components/room-tiles/TileHumidity.vue";
import { computed } from "vue";
import { useHistoryStore } from "../../stores/history";

const history = useHistoryStore();

const humidityByRoom = computed(() => {
  return Object.fromEntries(
    (history.airConditioningLog?.rooms ?? []).map((room) => [room.id, room.airConditioningLog]),
  );
});
</script>

<template>
  <RoomTiles>
    <template #default="{ room }">
      <TileHumidity
        :room="room"
        :humidity-log="humidityByRoom[room.id]"
      />
    </template>
  </RoomTiles>
</template>
