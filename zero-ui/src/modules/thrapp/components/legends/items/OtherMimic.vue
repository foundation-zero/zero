<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../mimics/data";
import { ExchangeCircuitInstance } from "../../../mimics/instances";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.otherMimic");
const circuit = getTooltipContext(MimicComponentType.ExchangeCircuit)("dhw:highTempLoop");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <ExchangeCircuitInstance v-bind="circuit" />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
