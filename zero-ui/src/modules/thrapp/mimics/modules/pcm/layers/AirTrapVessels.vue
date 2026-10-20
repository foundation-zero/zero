<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { AirTrapVesselInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { PCM_AIR_TRAP_VESSEL_DATA } from "../data";
</script>

<template>
  <g>
    <AirTrapVesselInstance
      x="200"
      y="-30"
      :orientation="ComponentOrientation.Up"
      v-bind="PCM_AIR_TRAP_VESSEL_DATA.AirTrapVessel['1084']"
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
