<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { PipeHeatExchangerState } from "../../../mimics/components/pipe-heat-exchanger";
import PipeHeatExchanger from "../../../mimics/components/pipe-heat-exchanger/PipeHeatExchanger.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.pipeHeatExchanger");
</script>

<template>
  <LegendItem>
    <LegendItemPreview class="gap-2">
      <PipeHeatExchanger :pump-state="PipeHeatExchangerState.Heating" />
      <PipeHeatExchanger :pump-state="PipeHeatExchangerState.Cooling" />
      <PipeHeatExchanger :pump-state="PipeHeatExchangerState.Idle" />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
