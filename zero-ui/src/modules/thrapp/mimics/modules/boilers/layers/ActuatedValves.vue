<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { ComponentOrientation } from "../../../components";
import { ActuatedValveType } from "../../../components/actuated-valve";
import { ActuatedValveInstance } from "../../../instances";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <ActuatedValveInstance
      x="361"
      y="156.2099609375"
      tag-id="1067-11"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank1Fill')"
    />
    <ActuatedValveInstance
      x="417"
      y="156.2099609375"
      tag-id="1067-12"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank1BoostingReturn')"
    />
    <ActuatedValveInstance
      x="472"
      y="156.2099609375"
      tag-id="1067-14"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank1BoostingSupply')"
    />
    <ActuatedValveInstance
      x="525"
      y="156.2099609375"
      tag-id="1067-13"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank1Empty')"
    />
    <ActuatedValveInstance
      x="715"
      y="156.2099609375"
      tag-id="1067-07"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank2Fill')"
    />
    <ActuatedValveInstance
      x="769"
      y="156.2099609375"
      tag-id="1067-08"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank2BoostingReturn')"
    />
    <ActuatedValveInstance
      x="824"
      y="156.2099609375"
      tag-id="1067-10"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank2BoostingSupply')"
    />
    <ActuatedValveInstance
      x="877"
      y="156.2099609375"
      tag-id="1067-09"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank2Empty')"
    />
    <ActuatedValveInstance
      x="1053"
      y="156.2099609375"
      tag-id="1067-03"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank3Fill')"
    />
    <ActuatedValveInstance
      x="1107"
      y="156.2099609375"
      tag-id="1067-04"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank3BoostingReturn')"
    />
    <ActuatedValveInstance
      x="1161"
      y="156.2099609375"
      tag-id="1067-06"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank3BoostingSupply')"
    />
    <ActuatedValveInstance
      x="1219"
      y="156.2099609375"
      tag-id="1067-05"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchTank3Empty')"
    />
    <ActuatedValveInstance
      x="1046"
      y="473.2099609375"
      tag-id="1064-08"
      :type="ActuatedValveType.FlowControl"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersFlowcontrolLt1')"
    />

    <ActuatedValveInstance
      x="1046"
      y="635"
      tag-id="1064-03"
      :type="ActuatedValveType.FlowControl"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersFlowcontrolLt2')"
    />
    <ActuatedValveInstance
      x="179.5"
      y="586.2099609375"
      tag-id="1067-17"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchHeatpump')"
    />
    <ActuatedValveInstance
      x="211"
      y="554"
      tag-id="1067-16"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchLowTemperature')"
    />
    <ActuatedValveInstance
      x="145"
      y="554"
      tag-id="1067-18"
      :type="ActuatedValveType.Switch"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'boilers', 'boilersSwitchHighTemperature')"
    />
  </g>
</template>
