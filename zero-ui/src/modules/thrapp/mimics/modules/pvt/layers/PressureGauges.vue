<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { PressureGaugeInstance } from "../../../instances";
</script>

<template>
  <g>
    <PressureGaugeInstance
      x="400"
      y="209"
      tag-id="1095-03"
      :orientation="ComponentOrientation.Right"
    />
    <PressureGaugeInstance
      x="400"
      y="367"
      tag-id="1095-04"
      :orientation="ComponentOrientation.Right"
    />
    <PressureGaugeInstance
      x="400"
      y="558"
      tag-id="1095-05"
      :orientation="ComponentOrientation.Right"
    />
  </g>
</template>
