<script setup lang="ts">
import { ZiAradexPropDrive, ZiPlug3 } from "@/modules/common/components/icons";
import { MimicComponentType } from "@/modules/thrapp/types";
import {
  PropulsionCoolerInstance,
  PropulsionDriveInstance,
  ShorePowerConverterInstance,
} from "../../../instances";
import { DRIVES_ASSET_DATA } from "../data";

const shorepower = DRIVES_ASSET_DATA[MimicComponentType.ShorePowerConverter].shorepower;
const propulsionDrives = DRIVES_ASSET_DATA[MimicComponentType.PropulsionDrive];
const propulsionCoolers = DRIVES_ASSET_DATA[MimicComponentType.PropulsionCooler];
</script>

<template>
  <PropulsionDriveInstance
    x="22"
    y="36"
    :height="196"
    dense
    v-bind="propulsionDrives.propdriveAft2"
  >
    <template #icon>
      <ZiAradexPropDrive />
    </template>
  </PropulsionDriveInstance>
  <PropulsionDriveInstance
    x="22"
    y="242"
    :height="196"
    dense
    v-bind="propulsionDrives.propdriveAft1"
  >
    <template #icon>
      <ZiAradexPropDrive />
    </template>
  </PropulsionDriveInstance>
  <PropulsionDriveInstance
    x="22"
    y="476"
    :height="196"
    dense
    v-bind="propulsionDrives.propdriveFwd2"
  >
    <template #icon>
      <ZiAradexPropDrive />
    </template>
  </PropulsionDriveInstance>
  <PropulsionDriveInstance
    x="22"
    y="682"
    :height="196"
    dense
    v-bind="propulsionDrives.propdriveFwd1"
  >
    <template #icon>
      <ZiAradexPropDrive />
    </template>
  </PropulsionDriveInstance>
  <PropulsionCoolerInstance
    x="614"
    y="286"
    :width="169"
    :height="158"
    dense
    v-bind="propulsionCoolers['1012']"
  />
  <PropulsionCoolerInstance
    x="614"
    y="729"
    :width="169"
    :height="158"
    dense
    v-bind="propulsionCoolers['1013']"
  />
  <ShorePowerConverterInstance
    x="881.1582"
    y="20.916"
    :height="222"
    v-bind="shorepower"
  >
    <template #icon>
      <ZiPlug3 class="size-6" />
    </template>
  </ShorePowerConverterInstance>
</template>
