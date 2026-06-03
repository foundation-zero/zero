<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { ComponentOrientation } from "../../../components";
import { PumpInstance } from "../../../instances";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <PumpInstance
      x="169.5"
      y="316"
      tag-id="1022"
      :pump="getField(SensorComponentType.Pump, 'boilers', 'boilersPump')"
      :orientation="ComponentOrientation.Down"
    />
  </g>
</template>
