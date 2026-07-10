<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import ThrusterInstance from "../../../instances/ThrusterInstance.vue";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <ThrusterInstance
      x="23"
      y="183"
      tag-id="1035"
      title-key="aftTitle"
      :source="getField(SensorComponentType.Thruster, 'thrusters', 'thrustersThrusterAft')"
      :mode-source="getField(SensorComponentType.Pcs, 'thrusters', 'thrustersPcs')"
      :temperature-source="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureAft')
      "
    />

    <ThrusterInstance
      x="23"
      y="441"
      tag-id="1035"
      title-key="fwdTitle"
      :source="getField(SensorComponentType.Thruster, 'thrusters', 'thrustersThrusterFwd')"
      :mode-source="getField(SensorComponentType.Pcs, 'thrusters', 'thrustersPcs')"
      :temperature-source="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureFwd')
      "
    />

    <rect
      x="1018"
      y="68"
      width="171.928"
      height="180.927"
      rx="12"
      class="stroke-background-muted fill-transparent"
      stroke-dasharray="4 4"
    />
  </g>
</template>
