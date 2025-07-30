<script setup lang="ts">
import RoomTiles from "@modules/admin/room-tiles/RoomTiles.vue";
import TileCO2 from "@modules/admin/room-tiles/TileCO2.vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">
    {{ t("labels.ventilation") }}
  </h1>
  <RoomTiles>
    <template #default="{ room }">
      <TileCO2 :room="room" />
    </template>
  </RoomTiles>
</template>
