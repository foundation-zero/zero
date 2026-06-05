<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import PressureSensor from "../../../mimics/components/pressure-sensor/PressureSensor.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.pressureSensors");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <PressureSensor />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
