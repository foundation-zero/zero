<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import HeatPumpInstance from "../../../mimics/instances/HeatPumpInstance.vue";
import { BOILERS_MIMIC_DATA } from "../../../mimics/modules/boilers/data";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.heatPump");
const assets = BOILERS_MIMIC_DATA[MimicComponentType.HeatPump];
</script>

<template>
  <LegendItem class="min-h-27">
    <LegendItemPreview>
      <HeatPumpInstance
        tag-id="1035"
        v-bind="assets['1035']"
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
