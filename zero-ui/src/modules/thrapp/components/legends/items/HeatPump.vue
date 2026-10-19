<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../mimics/data";
import HeatPumpInstance from "../../../mimics/instances/HeatPumpInstance.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.heatPump");
const heatPump = getTooltipContext(MimicComponentType.HeatPump)("1035");
</script>

<template>
  <LegendItem class="min-h-27">
    <LegendItemPreview>
      <HeatPumpInstance v-bind="heatPump" />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
