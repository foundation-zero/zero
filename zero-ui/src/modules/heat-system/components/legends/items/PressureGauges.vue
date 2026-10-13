<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import PressureGauge
  from "@/modules/heat-system/mimics/components/pressure-gauge/PressureGauge.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("heatSystem.legends.pressureGauges");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <PressureGauge />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
