<script setup lang="ts">
import { Room, Units, ValidationStatus } from "@/@types";
import RoomTiles from "@/components/admin/room-tiles/RoomTiles.vue";
import { formatInt } from "@/lib/utils";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const validate = (room: Room) => {
  if (room.actualCO2 >= 2000) {
    return ValidationStatus.FAIL;
  }

  if (room.actualCO2 >= 1000) {
    return ValidationStatus.WARN;
  }

  return ValidationStatus.OK;
};
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">
    {{ t("labels.ventilation") }}
  </h1>
  <RoomTiles :validate="validate">
    <template #center="{ room }">
      <span :class="{ 'max-md:text-rsm': room.actualCO2 >= 1000 }">{{
        formatInt(room.actualCO2)
      }}</span>
      <span class="ml-[0.2em] text-r3xs font-extralight">{{ Units.PPM }}</span>
    </template>
  </RoomTiles>
</template>
