<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PumpInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const pumps = THRUSTERS_MIMIC_DATA[MimicComponentType.Pump];
</script>

<template>
  <g>
    <PumpInstance
      x="696"
      y="513"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1194']"
    >
      <TagLabelInstance
        x="696"
        y="489"
        tag-id="1194"
      />
    </PumpInstance>
    <PumpInstance
      x="696"
      y="604"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1195']"
    >
      <TagLabelInstance
        x="696"
        y="581"
        tag-id="1195"
      />
    </PumpInstance>
  </g>
</template>
