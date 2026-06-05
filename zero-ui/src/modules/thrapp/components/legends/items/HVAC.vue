<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { SensorComponentType } from "@/modules/thrs/types";
import { RiSnowflakeLine } from "@remixicon/vue";
import HeatPumpInstance from "../../../mimics/instances/HeatPumpInstance.vue";
import { getField } from "../../../mimics/providers";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.hvac");
</script>

<template>
  <LegendItem class="min-h-27">
    <LegendItemPreview>
      <HeatPumpInstance
        :force-height="false"
        tag-id="41001001"
        :title="t('assetTitle')"
        :icon="RiSnowflakeLine"
        :heat-exchanger="
          getField(SensorComponentType.HeatExchanger, 'boilers', 'boilersHvacExchanger')
        "
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
