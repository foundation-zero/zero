<script setup lang="ts">
import RoomTiles from "@/components/admin/room-tiles/RoomTiles.vue";
import { randomHumidity } from "@/lib/utils";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">{{ t("labels.humidity") }}</h1>
  <RoomTiles>
    <template #center>
      <span>{{ randomHumidity() }}</span>
      <span class="ml-2 text-rxs font-extralight">&percnt;</span>
    </template>
  </RoomTiles>
</template>
