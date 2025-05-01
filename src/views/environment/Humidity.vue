<script setup lang="ts">
import { Room, ValidateFn, ValidationStatus } from "@/@types";
import RoomTiles from "@/components/admin/room-tiles/RoomTiles.vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const validate: ValidateFn<Room> = (room) => {
  const value = Number(room.actualHumidity);

  if (value > 60 || value < 35) {
    return ValidationStatus.WARN;
  }

  return ValidationStatus.OK;
};
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">{{ t("labels.humidity") }}</h1>
  <RoomTiles :validate="validate">
    <template #center="{ room }">
      <span>{{ room.actualHumidity.toFixed(0) }}</span>
      <span class="ml-[0.25em] text-r2xs font-extralight">&percnt;</span>
    </template>
  </RoomTiles>
</template>
