<script setup lang="ts">
import RoomTiles from "@/modules/domestic/admin/components/room-tiles/RoomTiles.vue";
import TileCO2 from "@/modules/domestic/admin/components/room-tiles/TileCO2.vue";
import { computed } from "vue";
import { useHistoryStore } from "../../stores/history";

const history = useHistoryStore();

const ventilationByRoom = computed(() => {
  return Object.fromEntries(
    (history.ventilationLog?.rooms ?? []).map((room) => [room.id, room.ventilationLog]),
  );
});
</script>

<template>
  <RoomTiles>
    <template #default="{ room }">
      <TileCO2
        :room="room"
        :ventilation-log="ventilationByRoom[room.id]"
      />
    </template>
  </RoomTiles>
</template>
