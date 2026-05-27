<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import BoilerTankInstance from "../../../instances/BoilerTankInstance.vue";
import { getField } from "../../../instances/index.ts";
</script>

<template>
  <g>
    <BoilerTankInstance
      x="355"
      y="0"
      title="Tank 1"
      tag-id="1053"
      :level="getField(SensorComponentType.Level, 'boilers', 'boilersLevelTank1')"
      :temperature="getField(SensorComponentType.Temperature, 'boilers', 'boilersTemperatureTank1')"
    />

    <BoilerTankInstance
      x="718"
      y="0"
      title="Tank 2"
      tag-id="1054"
      :level="getField(SensorComponentType.Level, 'boilers', 'boilersLevelTank2')"
      :temperature="getField(SensorComponentType.Temperature, 'boilers', 'boilersTemperatureTank2')"
    />

    <BoilerTankInstance
      x="1056"
      y="0"
      title="Tank 3"
      tag-id="1055"
      :level="getField(SensorComponentType.Level, 'boilers', 'boilersLevelTank3')"
      :temperature="getField(SensorComponentType.Temperature, 'boilers', 'boilersTemperatureTank3')"
    />
  </g>
</template>
