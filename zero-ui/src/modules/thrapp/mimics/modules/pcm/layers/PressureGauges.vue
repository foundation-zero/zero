<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { PCM_MIMIC_DATA } from "../data";

const pressureGauges = PCM_MIMIC_DATA[MimicComponentType.PressureGauge];
</script>

<template>
  <g>
    <PressureGaugeInstance
      x="78"
      y="130"
      :orientation="ComponentOrientation.Right"
      v-bind="pressureGauges['1095-06']"
    >
      <TagLabelInstance
        x="40"
        y="130"
        :tag-id="pressureGauges['1095-06'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
    <PressureGaugeInstance
      x="297"
      y="775"
      :orientation="ComponentOrientation.Right"
      v-bind="pressureGauges['1096-09']"
    >
      <TagLabelInstance
        :target-x="275"
        y="775"
        :tag-id="pressureGauges['1096-09'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </g>
</template>
