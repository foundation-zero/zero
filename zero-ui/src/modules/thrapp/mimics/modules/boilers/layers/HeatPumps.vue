<script setup lang="ts">
import { RiSnowflakeLine, RiTempHotLine } from "@remixicon/vue";
import HeatPumpInstance from "../../../instances/HeatPumpInstance.vue";
</script>

<template>
  <g>
    <HeatPumpInstance
      x="70"
      y="656"
      :width="200"
      :height="164"
      tag-id="1035"
      title="Heat Pump"
      :icon="RiTempHotLine"
    />

    <HeatPumpInstance
      x="670"
      y="400"
      :width="150"
      :height="164"
      tag-id="41001001"
      title="HVAC"
      :icon="RiSnowflakeLine"
    />
  </g>
</template>
