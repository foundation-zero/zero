<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import FlowSensor from "../../../mimics/components/flow-sensor/FlowSensor.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend/";

const t = tScoped("thrapp.legends.flowSensors");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <FlowSensor class="-ml-1" />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
