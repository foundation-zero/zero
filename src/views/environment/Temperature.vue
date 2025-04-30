<script setup lang="ts">
import RoomTiles from "@/components/admin/room-tiles/RoomTiles.vue";
import { randomHumidity } from "@/lib/utils";
import { Droplets } from "lucide-vue-next";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">
    {{ t("labels.temperature") }}
  </h1>
  <RoomTiles>
    <template #center="{ room }">
      <span>{{ room.actualTemperature.toFixed(0) }}</span>
      <sup class="top-[-0.3em] text-rxs font-extralight">&deg;</sup>
    </template>

    <template #bottom-left>
      <Droplets class="inline h-[1.1em] w-[1.1em] text-primary/80" />
      <span>
        <span class="ml-2 text-rlg font-bold">{{ randomHumidity() }}</span>
        <span class="ml-0.5 text-rsm text-primary/80">&percnt;</span>
      </span>
    </template>

    <template #bottom-right="{ room }">
      <span>
        <span class="text-rsm text-primary/80">Set to</span>
        <span class="ml-1 text-rlg font-bold text-primary">
          {{ room.temperatureSetpoint }}
        </span>
        <sup class="text-rxs font-extralight">&deg;</sup>
      </span>
    </template>
  </RoomTiles>
</template>
