<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const manualPressureSensors = getTooltipContexts(MimicComponentType.PressureGauge, ["1095-14"]);
</script>

<template>
  <g>
    <PressureGaugeInstance
      x="197"
      y="423.2099609375"
      :orientation="ComponentOrientation.Left"
      v-bind="manualPressureSensors['1095-14']"
    >
      <TagLabelInstance
        x="236"
        y="425"
        :tag-id="manualPressureSensors['1095-14'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </g>
</template>
