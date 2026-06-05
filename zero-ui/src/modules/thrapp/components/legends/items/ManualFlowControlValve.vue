<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { ManualValveType } from "@/modules/thrapp/mimics/components/manual-valve/index.ts";
import ManualValve from "@/modules/thrapp/mimics/components/manual-valve/ManualValve.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.manualFlowControlValve");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <ManualValve :type="ManualValveType.FlowControl" />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
