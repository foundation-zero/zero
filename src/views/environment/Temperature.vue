<script setup lang="ts">
import { Room, ValidationStatus } from "@/@types";
import RoomTiles from "@/components/admin/room-tiles/RoomTiles.vue";
import { Droplets } from "lucide-vue-next";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const validate = (room: Room) => {
  const value = Number(room.actualTemperature);

  if (value >= 25) {
    return ValidationStatus.WARN;
  }

  return ValidationStatus.OK;
};
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">
    {{ t("labels.temperature") }}
  </h1>
  <RoomTiles :validate="validate">
    <template #center="{ room }">
      <span>{{ room.actualTemperature.toFixed(0) }}</span>
      <sup class="top-[-0.3em] text-rxs font-extralight">&deg;</sup>
    </template>

    <template #bottom-left="{ room }">
      <Droplets class="inline h-[1em] w-[1em]" />
      <span>
        <span class="ml-[0.5em] font-extrabold">{{ room.actualHumidity.toFixed(0) }}</span>
        <span class="ml-[0.25em] text-rsm font-extralight">&percnt;</span>
      </span>
    </template>

    <template #bottom-right="{ room }">
      <span>
        <span class="text-rsm font-light">Set to</span>
        <span class="ml-[0.25em] font-extrabold">
          {{ room.temperatureSetpoint }}
        </span>
        <sup class="font-extralight">&deg;</sup>
      </span>
    </template>
  </RoomTiles>
</template>
