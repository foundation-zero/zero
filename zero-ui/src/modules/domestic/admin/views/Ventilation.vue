<script setup lang="ts">
import RoomTiles from "@/modules/domestic/admin/components/room-tiles/RoomTiles.vue";
import TileCO2 from "@/modules/domestic/admin/components/room-tiles/TileCO2.vue";
<<<<<<< HEAD
=======
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useHistoryStore } from "../../stores/history";

const { t } = useI18n();
const history = useHistoryStore();

const ventilationByRoom = computed(() => {
  return Object.fromEntries(
    (history.ventilationLog?.rooms ?? []).map((room) => [room.id, room.ventilationLog]),
  );
});
>>>>>>> 4c2e4b7c (Free Domestic from RisingWave)
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
