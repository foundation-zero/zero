<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import {
  PropulsionCoolerInstance,
  PropulsionDriveInstance,
  ShorePowerConverterInstance,
} from "../../../instances";

const shorePowerConverters = getTooltipContexts(MimicComponentType.ShorePowerConverter, [
  "drives:shorepower",
]);
const propulsionDrives = getTooltipContexts(MimicComponentType.PropulsionDrive, [
  "drives:propdriveAft1",
  "drives:propdriveAft2",
  "drives:propdriveFwd1",
  "drives:propdriveFwd2",
]);
const propulsionCoolers = getTooltipContexts(MimicComponentType.PropulsionCooler, ["1012", "1013"]);
</script>

<template>
  <PropulsionDriveInstance
    x="22"
    y="36"
    :height="196"
    v-bind="propulsionDrives['drives:propdriveAft2']"
  />
  <PropulsionDriveInstance
    x="22"
    y="242"
    :height="196"
    v-bind="propulsionDrives['drives:propdriveAft1']"
  />
  <PropulsionDriveInstance
    x="22"
    y="476"
    :height="196"
    v-bind="propulsionDrives['drives:propdriveFwd2']"
  />
  <PropulsionDriveInstance
    x="22"
    y="682"
    :height="196"
    v-bind="propulsionDrives['drives:propdriveFwd1']"
  />
  <PropulsionCoolerInstance
    x="614"
    y="286"
    :width="169"
    :height="158"
    v-bind="propulsionCoolers['1012']"
  />
  <PropulsionCoolerInstance
    x="614"
    y="729"
    :width="169"
    :height="158"
    v-bind="propulsionCoolers['1013']"
  />
  <ShorePowerConverterInstance
    x="881.1582"
    y="20.916"
    :height="222"
    v-bind="shorePowerConverters['drives:shorepower']"
  />
</template>
