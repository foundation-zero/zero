<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { PyranometerDotInstance } from "../../../instances";

const pyranometers = getTooltipContexts(MimicComponentType.Pyranometer, ["9043", "9044"]);
</script>

<template>
  <g>
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
