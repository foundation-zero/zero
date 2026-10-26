<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { IrradianceLabelInstance, PyranometerInstance } from "../../../instances";

const pyranometers = getTooltipContexts(MimicComponentType.Pyranometer, ["9044", "9043"]);
</script>

<template>
  <g>
    <PyranometerInstance
      x="11"
      y="175.5"
      v-bind="pyranometers['9044']"
    />
    <IrradianceLabelInstance
      x="1"
      y="197"
      :source="pyranometers['9044'].source"
      :tag-id="pyranometers['9044'].tooltip?.yardTag"
    />

    <PyranometerInstance
      x="8"
      y="367.5"
      v-bind="pyranometers['9043']"
    />
    <IrradianceLabelInstance
      x="1"
      y="390"
      :source="pyranometers['9043'].source"
      :tag-id="pyranometers['9043'].tooltip?.yardTag"
    />
  </g>
</template>
