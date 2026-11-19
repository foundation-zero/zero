<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import ActuatedValve from "../../../components/actuated-valve/ActuatedValve.vue";
import MixValve from "../../../components/actuated-valve/MixValve.vue";
import TwoWayValve from "../../../components/actuated-valve/TwoWayValve.vue";
</script>

<template>
  <!-- Each converter drives its own return valve; the valves report nothing, so they are drawn
  without data. -->
  <g>
    <ActuatedValve
      x="275.63"
      y="169.41"
      :orientation="ComponentOrientation.Up"
    >
      <TwoWayValve :flow="0" />
      <MixValve />
    </ActuatedValve>
    <ActuatedValve
      x="275.63"
      y="382.41"
      :orientation="ComponentOrientation.Up"
    >
      <TwoWayValve :flow="0" />
      <MixValve />
    </ActuatedValve>
    <ActuatedValve
      x="275.63"
      y="592.41"
      :orientation="ComponentOrientation.Up"
    >
      <TwoWayValve :flow="0" />
      <MixValve />
    </ActuatedValve>
    <ActuatedValve
      x="275.63"
      y="788.41"
      :orientation="ComponentOrientation.Up"
    >
      <TwoWayValve :flow="0" />
      <MixValve />
    </ActuatedValve>
  </g>
</template>
