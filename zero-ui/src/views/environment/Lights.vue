<script setup lang="ts">
import RoomsToggle from "@modules/admin/room-tiles/RoomsToggle.vue";
import RoomTiles from "@modules/admin/room-tiles/RoomTiles.vue";
import TileLights from "@modules/admin/room-tiles/TileLights.vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">
    {{ t("labels.lights") }}
  </h1>
  <RoomTiles>
    <template #header="{ area }">
      <RoomsToggle :rooms="area.rooms" />
    </template>
    <template #default="{ room }">
      <TileLights :room="room" />
    </template>
  </RoomTiles>
</template>
