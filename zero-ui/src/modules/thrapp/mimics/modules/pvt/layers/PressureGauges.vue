<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_GAUGE_WIDTH } from "../../../components/pressure-gauge";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { PVT_MIMIC_DATA } from "../data";

const pressureGauges = PVT_MIMIC_DATA[MimicComponentType.PressureGauge];
</script>

<template>
  <g>
    <PressureGaugeInstance
      x="400"
      y="190"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureGauges['1095-03']"
    >
      <TagLabelInstance
        :target-x="400"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="175"
        :tag-id="pressureGauges['1095-03'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
    <PressureGaugeInstance
      x="400"
      y="387"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureGauges['1095-04']"
    >
      <TagLabelInstance
        :target-x="400"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="372"
        :tag-id="pressureGauges['1095-04'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
    <PressureGaugeInstance
      x="400"
      y="611"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureGauges['1095-05']"
    >
      <TagLabelInstance
        :target-x="400"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="597"
        :tag-id="pressureGauges['1095-05'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </g>
</template>
