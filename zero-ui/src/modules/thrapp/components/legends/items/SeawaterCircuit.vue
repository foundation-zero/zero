<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../mimics/data";
import { SeawaterCircuitInstance } from "../../../mimics/instances";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.seawaterCircuit");
const context = getTooltipContext(MimicComponentType.SeawaterCircuit)("pvt:seawater");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <SeawaterCircuitInstance
        v-bind="context"
        width="194"
        height="90"
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
