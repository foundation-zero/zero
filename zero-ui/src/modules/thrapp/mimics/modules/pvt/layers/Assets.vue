<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { PvtInstance } from "../../../instances";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <PvtInstance
      x="14"
      y="30"
      tag-id="9002-01"
      title-key="fwdTitle"
      :pump-source="getField(SensorComponentType.Pump, 'pvt', 'pvtPumpMainFwd')"
      :flow-source="getField(SensorComponentType.Flow, 'pvt', 'pvtFlowMainFwdRecovery')"
      :return-temperature-source="
        getField(SensorComponentType.Temperature, 'pvt', 'pvtTemperatureMainFwdReturn')
      "
      :supply-temperature-source="
        getField(SensorComponentType.Temperature, 'pvt', 'pvtTemperatureMainFwdSupply')
      "
    />

    <PvtInstance
      x="14"
      y="241"
      tag-id="9002-02"
      title-key="aftTitle"
      :pump-source="getField(SensorComponentType.Pump, 'pvt', 'pvtPumpMainAft')"
      :flow-source="getField(SensorComponentType.Flow, 'pvt', 'pvtFlowMainAftRecovery')"
      :return-temperature-source="
        getField(SensorComponentType.Temperature, 'pvt', 'pvtTemperatureMainAftReturn')
      "
      :supply-temperature-source="
        getField(SensorComponentType.Temperature, 'pvt', 'pvtTemperatureMainAftSupply')
      "
    />

    <PvtInstance
      x="14"
      y="455"
      tag-id="9002-01"
      title-key="ownersTitle"
      :pump-source="getField(SensorComponentType.Pump, 'pvt', 'pvtPumpOwners')"
      :flow-source="getField(SensorComponentType.Flow, 'pvt', 'pvtFlowOwnersRecovery')"
      :return-temperature-source="
        getField(SensorComponentType.Temperature, 'pvt', 'pvtTemperatureOwnersReturn')
      "
      :supply-temperature-source="
        getField(SensorComponentType.Temperature, 'pvt', 'pvtTemperatureOwnersSupply')
      "
    />

    <rect
      x="1137"
      y="111"
      width="155"
      height="168"
      rx="12"
      class="stroke-background-muted fill-transparent"
      stroke-dasharray="4 4"
    />
  </g>
</template>
