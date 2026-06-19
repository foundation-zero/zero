<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import { LoopCircuitInstance } from "../../../mimics/instances";
import { BOILERS_MIMIC_DATA } from "../../../mimics/modules/boilers/data";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.otherMimic");
const circuits = BOILERS_MIMIC_DATA[MimicComponentType.ExchangeCircuit];
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <LoopCircuitInstance v-bind="circuits['highTempLoop']" />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
