<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import ThrusterInstance from "../../../instances/ThrusterInstance.vue";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <ThrusterInstance
      x="23"
      y="143"
      title-key="aftTitle"
      :source="getField(SensorComponentType.Thruster, 'thrusters', 'thrustersThrusterAft')"
      :mode-source="getField(SensorComponentType.Pcs, 'thrusters', 'thrustersPcs')"
      :temperature-source="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureAft')
      "
    />

    <ThrusterInstance
      x="23"
      y="401"
      title-key="fwdTitle"
      :source="getField(SensorComponentType.Thruster, 'thrusters', 'thrustersThrusterFwd')"
      :mode-source="getField(SensorComponentType.Pcs, 'thrusters', 'thrustersPcs')"
      :temperature-source="
        getField(SensorComponentType.Temperature, 'thrusters', 'thrustersTemperatureFwd')
      "
    />
  </g>
</template>
