<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import { RiSnowflakeLine, RiTempHotLine } from "@remixicon/vue";
import HeatPumpInstance from "../../../instances/HeatPumpInstance.vue";
import { getField } from "../../../providers/index.ts";

const t = tScoped("thrapp.mimics.boilers.assets");
</script>

<template>
  <g>
    <HeatPumpInstance
      x="70"
      y="656"
      :width="200"
      :height="164"
      force-height
      tag-id="1035"
      :title="t('heatPumpTitle')"
      :icon="RiTempHotLine"
      :heat-exchanger="getField(SensorComponentType.HeatExchanger, 'boilers', 'boilersHeatpump')"
    />

    <HeatPumpInstance
      x="670"
      y="400"
      :width="150"
      :height="140"
      force-height
      tag-id="41001001"
      :title="t('hvacTitle')"
      hide-mode
      :icon="RiSnowflakeLine"
      :heat-exchanger="
        getField(SensorComponentType.HeatExchanger, 'boilers', 'boilersHvacExchanger')
      "
    />
  </g>
</template>
