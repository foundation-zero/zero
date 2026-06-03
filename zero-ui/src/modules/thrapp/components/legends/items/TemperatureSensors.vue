<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import TemperatureSensor from "../../../mimics/components/temperature-sensor/TemperatureSensor.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.temperatureSensors");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <TemperatureSensor />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
