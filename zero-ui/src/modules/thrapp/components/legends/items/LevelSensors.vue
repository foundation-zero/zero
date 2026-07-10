<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import LevelSensor from "../../../mimics/components/level-sensor/LevelSensor.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.levelSensors");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <LevelSensor />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
