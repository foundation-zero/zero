<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { SensorComponentType } from "@/modules/thrs/types";
import { RiTempHotLine } from "@remixicon/vue";
import { getField } from "../../..//mimics/providers";
import HeatPumpInstance from "../../../mimics/instances/HeatPumpInstance.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.heatPump");
</script>

<template>
  <LegendItem class="min-h-27">
    <LegendItemPreview>
      <HeatPumpInstance
        tag-id="1035"
        :title="t('assetTitle')"
        :icon="RiTempHotLine"
        :heat-exchanger="getField(SensorComponentType.HeatExchanger, 'boilers', 'boilersHeatpump')"
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
