<script setup lang="ts">
import { isDefined } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import type { SolarPanelStringProps } from "../components/solar-panel-string";
import { SolarPanelString } from "../components/solar-panel-string";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  SolarPanelStringProps &
    TooltipComponentContext<MimicComponentType.PvtString> & {
      /** Peak heat of the whole string in W, which colours its panels at full yield. */
      peakHeat: number;
    }
>();

const { t } = useI18n();

const { getSensorValue } = getMimicDataProvider();
const heatTransfer = getSensorValue(props.source);
const yieldRatio = computed(() => {
  const heat = heatTransfer.value?.heat?.value;
  return isDefined(heat) ? heat / props.peakHeat : undefined;
});
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <SolarPanelString
      :frame="frame"
      :panels="panels"
      :label="label"
      :yield-ratio="yieldRatio"
    >
      {{ t("thrapp.mimics.pvt.string", { label: tooltip?.yardTag }) }}
    </SolarPanelString>
  </MimicTooltipTrigger>
</template>
