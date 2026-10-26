<script setup lang="ts">
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import type { SolarPanelStringProps } from "../components/solar-panel-string";
import { SolarPanelString } from "../components/solar-panel-string";

const props = defineProps<
  SolarPanelStringProps & TooltipComponentContext<MimicComponentType.PvtString>
>();
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <SolarPanelString
      :frame="frame"
      :panels="panels"
      :label="label"
      :yield-ratio="yieldRatio"
    >
      String {{ custom.label }}
    </SolarPanelString>
  </MimicTooltipTrigger>
</template>
