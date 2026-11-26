<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { BiminiOutline } from "../../../components/bimini-outline";
import { toBiminiStringProps } from "../../../components/mini-map";
import { getTooltipContexts } from "../../../data";
import { PyranometerDotInstance, SolarPanelStringInstance } from "../../../instances";
import { MAIN_BIMINI_STRINGS } from "../layout";

// The top-down view of the main bimini, without overlays: those belong to the interactive bimini.
const strings = toBiminiStringProps(MAIN_BIMINI_STRINGS);

const pyranometers = getTooltipContexts(MimicComponentType.Pyranometer, ["9043", "9044"]);
</script>

<template>
  <g>
    <BiminiOutline />
    <SolarPanelStringInstance
      v-for="(string, index) in strings"
      :key="index"
      v-bind="string"
    />
    <PyranometerDotInstance
      x="54.41"
      y="386.58"
      v-bind="pyranometers['9043']"
    />
    <PyranometerDotInstance
      x="219.41"
      y="386.58"
      v-bind="pyranometers['9044']"
    />
  </g>
</template>
