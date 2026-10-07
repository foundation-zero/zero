<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { PRESSURE_GAUGE_WIDTH } from "../../../components/pressure-gauge";
import { PressureGaugeInstance, TagLabelInstance } from "../../../instances";
import { DRIVES_PRESSURE_GAUGE_DATA } from "../data";

const pressureGauges = DRIVES_PRESSURE_GAUGE_DATA.PressureGauge;
</script>

<template>
  <g>
    <PressureGaugeInstance
      x="1671"
      y="158.5"
      :orientation="ComponentOrientation.Right"
      v-bind="pressureGauges['1096-05']"
    >
      <TagLabelInstance
        x="1621"
        y="160"
        :tag-id="pressureGauges['1096-05'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
    <PressureGaugeInstance
      x="1232"
      y="579.916"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureGauges['1095-13']"
    >
      <TagLabelInstance
        target-x="1232"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="618"
        :tag-id="pressureGauges['1095-13'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </g>
</template>
