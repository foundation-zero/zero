<script setup lang="ts">
import { SensorState } from "@/components/environment/sensor-state";

import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <h1 class="mb-6 text-4xl font-bold md:mb-12 md:text-6xl">
    {{ t("labels.overview") }}
  </h1>
  <SensorState />
</template>
