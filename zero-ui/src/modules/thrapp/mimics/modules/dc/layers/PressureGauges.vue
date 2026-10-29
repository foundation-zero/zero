<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const pressureGauges = getTooltipContexts(MimicComponentType.PressureGauge, [
  "1095-10",
  "1095-11",
  "1095-12",
  "1096-06",
]);
</script>

<template>
  <PressureGaugeInstance
    x="377"
    y="166.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="pressureGauges['1095-10']"
  >
    <TagLabelInstance
      x="370"
      y="135.146"
      :tag-id="pressureGauges['1095-10'].tooltip?.yardTag"
    />
  </PressureGaugeInstance>
  <PressureGaugeInstance
    x="377"
    y="380.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="pressureGauges['1095-11']"
  >
    <TagLabelInstance
      x="370"
      y="350.146"
      :tag-id="pressureGauges['1095-11'].tooltip?.yardTag"
    />
  </PressureGaugeInstance>
  <PressureGaugeInstance
    x="377"
    y="610.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="pressureGauges['1095-12']"
  >
    <TagLabelInstance
      x="370"
      y="578.146"
      :tag-id="pressureGauges['1095-12'].tooltip?.yardTag"
    />
  </PressureGaugeInstance>
  <PressureGaugeInstance
    x="425.1"
    y="280.15"
    :orientation="ComponentOrientation.Left"
    v-bind="pressureGauges['1096-06']"
  >
    <TagLabelInstance
      x="461"
      y="281"
      :tag-id="pressureGauges['1096-06'].tooltip?.yardTag"
    />
  </PressureGaugeInstance>
</template>
