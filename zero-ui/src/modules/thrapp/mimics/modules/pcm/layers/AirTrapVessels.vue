<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { AirTrapVessel } from "../../../components/air-trap-vessel";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
</script>

<template>
  <g>
    <AirTrapVessel
      x="200"
      y="-30"
      :orientation="ComponentOrientation.Up"
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
