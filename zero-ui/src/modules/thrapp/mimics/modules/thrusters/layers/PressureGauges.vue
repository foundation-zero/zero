<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_GAUGE_WIDTH } from "../../../components/pressure-gauge";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const manualPressureSensors = THRUSTERS_MIMIC_DATA[MimicComponentType.PressureGauge];
</script>

<template>
  <g>
    <PressureGaugeInstance
      x="518"
      y="229"
      :orientation="ComponentOrientation.Down"
      v-bind="manualPressureSensors['1095-01']"
      ><TagLabelInstance
        :target-x="518"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="213"
        :tag-id="manualPressureSensors['1095-01'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </g>
</template>
