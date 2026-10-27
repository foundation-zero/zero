<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import type { SolarPanelStringProps } from "../components/solar-panel-string";
import { SolarPanelString } from "../components/solar-panel-string";

const props = defineProps<
  SolarPanelStringProps & TooltipComponentContext<MimicComponentType.PvtString>
>();

const { t } = useI18n();
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <SolarPanelString
      :frame="frame"
      :panels="panels"
      :label="label"
      :yield-ratio="yieldRatio"
    >
      {{ t("thrapp.mimics.pvt.string", { label: custom.label }) }}
    </SolarPanelString>
  </MimicTooltipTrigger>
</template>
