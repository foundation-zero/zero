<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { DHW_MIMIC_DATA } from "../data";

const manualPressureSensors = DHW_MIMIC_DATA[MimicComponentType.PressureGauge];
</script>

<template>
  <g>
    <PressureGaugeInstance
      x="197"
      y="423.2099609375"
      tag-id="1095-14"
      :orientation="ComponentOrientation.Left"
      v-bind="manualPressureSensors['1095-14']"
    >
      <TagLabelInstance
        x="236"
        y="432"
        tag-id="1095-14"
      />
    </PressureGaugeInstance>
  </g>
</template>
