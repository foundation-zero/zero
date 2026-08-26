<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import HeatPumpInstance from "../../../mimics/instances/HeatPumpInstance.vue";
import { DHW_MIMIC_DATA } from "../../../mimics/modules/dhw/data/index.ts";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.heatPump");
const assets = DHW_MIMIC_DATA[MimicComponentType.HeatPump];
</script>

<template>
  <LegendItem class="min-h-27">
    <LegendItemPreview>
      <HeatPumpInstance v-bind="assets['1035']" />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
