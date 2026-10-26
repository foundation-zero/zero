<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { AirTrapVesselInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const airTrapVessels = getTooltipContexts(MimicComponentType.AirTrapVessel, ["1084"]);
</script>

<template>
  <g>
    <AirTrapVesselInstance
      x="200"
      y="-30"
      :orientation="ComponentOrientation.Up"
      v-bind="airTrapVessels['1084']"
    />
    <TagLabelInstance
      x="230"
      y="-30"
      tag-id="1084"
    />
    <TagLabelInstance
      x="160"
      y="5"
      tag-id="1086"
    />
  </g>
</template>
