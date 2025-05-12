<script setup lang="ts">
import RoomTiles from "@/components/admin/room-tiles/RoomTiles.vue";
import TileHumidity from "@/components/admin/room-tiles/TileHumidity.vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">{{ t("labels.humidity") }}</h1>
  <RoomTiles>
    <template #default="{ room }">
      <TileHumidity :room="room" />
    </template>
  </RoomTiles>
</template>
