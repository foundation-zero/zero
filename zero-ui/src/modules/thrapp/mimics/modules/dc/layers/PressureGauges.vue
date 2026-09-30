<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { DC_PRESSURE_GAUGE_DATA } from "../data";

const pressureGauges = DC_PRESSURE_GAUGE_DATA[MimicComponentType.PressureGauge];
</script>

<template>
  <PressureGaugeInstance
    x="377"
    y="166.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="pressureGauges['1095-10']"
  >
    <TagLabelInstance
      x="376"
      y="141.1458"
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
      x="376"
      y="356.1458"
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
      x="376"
      y="584.1458"
      :tag-id="pressureGauges['1095-12'].tooltip?.yardTag"
    />
  </PressureGaugeInstance>
  <PressureGaugeInstance
    x="1159.4043"
    y="556.1458"
    :orientation="ComponentOrientation.Left"
    v-bind="pressureGauges['1096-06']"
  >
    <TagLabelInstance
      x="1196.1406"
      y="559.1458"
      :tag-id="pressureGauges['1096-06'].tooltip?.yardTag"
    />
  </PressureGaugeInstance>
</template>
