<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { SensorComponentType } from "@/modules/thrs/types";
import { LoopCircuitInstance } from "../../../mimics/instances";
import { getField } from "../../../mimics/providers";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.otherMimic");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <LoopCircuitInstance
        :title="t('assetTitle')"
        :delta-t="getField(SensorComponentType.DeltaT, 'boilers', 'consumersDelta')"
        :flow="getField(SensorComponentType.Flow, 'boilers', 'consumersFlowBoosting')"
        :t-in="
          getField(SensorComponentType.Temperature, 'boilers', 'consumersTemperatureBoostingSupply')
        "
        :t-out="
          getField(SensorComponentType.Temperature, 'boilers', 'consumersTemperatureBoostingReturn')
        "
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
