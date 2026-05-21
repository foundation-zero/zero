<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { LevelSensorInstance } from "../../../instances";
</script>

<template>
  <g>
    <LevelSensorInstance
      x="560.0000076293945"
      y="10.2178955078125"
      tag-id="1098-01"
      :orientation="ComponentOrientation.Left"
    />
    <LevelSensorInstance
      x="920.0806884765625"
      y="10.2178955078125"
      tag-id="1098-02"
      :orientation="ComponentOrientation.Left"
    />
    <LevelSensorInstance
      x="1260.0806884765625"
      y="10.2178955078125"
      tag-id="1098-03"
      :orientation="ComponentOrientation.Left"
    />
  </g>
</template>
