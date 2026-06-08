<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { ComponentOrientation } from "../../../components";
import { FlowControlValveInstance, SwitchValveInstance } from "../../../instances";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <SwitchValveInstance
      x="361"
      y="156.2099609375"
      tag-id="1067-11"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank1Fill')"
    />
    <SwitchValveInstance
      x="417"
      y="156.2099609375"
      tag-id="1067-12"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank1BoostingReturn')"
    />
    <SwitchValveInstance
      x="472"
      y="156.2099609375"
      tag-id="1067-14"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank1BoostingSupply')"
    />
    <SwitchValveInstance
      x="525"
      y="156.2099609375"
      tag-id="1067-13"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank1Empty')"
    />
    <SwitchValveInstance
      x="715"
      y="156.2099609375"
      tag-id="1067-07"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank2Fill')"
    />
    <SwitchValveInstance
      x="769"
      y="156.2099609375"
      tag-id="1067-08"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank2BoostingReturn')"
    />
    <SwitchValveInstance
      x="824"
      y="156.2099609375"
      tag-id="1067-10"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank2BoostingSupply')"
    />
    <SwitchValveInstance
      x="877"
      y="156.2099609375"
      tag-id="1067-09"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank2Empty')"
    />
    <SwitchValveInstance
      x="1053"
      y="156.2099609375"
      tag-id="1067-03"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank3Fill')"
    />
    <SwitchValveInstance
      x="1107"
      y="156.2099609375"
      tag-id="1067-04"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank3BoostingReturn')"
    />
    <SwitchValveInstance
      x="1161"
      y="156.2099609375"
      tag-id="1067-06"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank3BoostingSupply')"
    />
    <SwitchValveInstance
      x="1219"
      y="156.2099609375"
      tag-id="1067-05"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank3Empty')"
    />

    <SwitchValveInstance
      x="179.5"
      y="586.2099609375"
      tag-id="1067-17"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchHeatpump')"
    />
    <SwitchValveInstance
      x="211"
      y="554"
      tag-id="1067-16"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchLowTemperature')"
    />
    <SwitchValveInstance
      x="145"
      y="554"
      tag-id="1067-18"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchHighTemperature')"
    />

    <FlowControlValveInstance
      x="1046"
      y="473.2099609375"
      tag-id="1064-08"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersFlowcontrolLt1')"
    />

    <FlowControlValveInstance
      x="1046"
      y="635"
      tag-id="1064-03"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersFlowcontrolLt2')"
    />
  </g>
</template>
