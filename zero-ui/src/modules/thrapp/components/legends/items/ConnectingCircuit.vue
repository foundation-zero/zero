<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../mimics/data";
import { ConnectingCircuitInstance } from "../../../mimics/instances";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.connectingCircuit");
const context = getTooltipContext(MimicComponentType.ConnectingCircuit)("pvt:pcm");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <ConnectingCircuitInstance
        v-bind="context"
        width="194"
        height="195"
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
