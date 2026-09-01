<script setup lang="ts">
import { SolarPanelIcon } from "@/modules/common/components/icons";
import { PvtMode as PvtModeEnum } from "@/modules/thrsim/types";
import { RiDropLine, RiFireLine, RiFlashlightLine } from "@remixicon/vue";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { Pvt, PvtMode, PvtTitle } from "../components/pvt";
import { ValueList, ValueListItem, ValueListSeparator } from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider } from "../providers";
import { FieldRenderer } from "../renderers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.Pvt> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  {
    width: 220,
    height: 228,
    forceHeight: true,
  },
);

const { t } = useI18n();
const { getSensorValue, getComponentState, getControllerState } = getMimicDataProvider();

const controller = getControllerState(props.controllerState.controller);
const flow = getSensorValue(props.sensors.flow);
const pvt = getSensorValue(props.source);
const state = getComponentState();

const flowRate = computed(() => {
  return flow.value?.flow?.value;
});

const modeKey = computed(() => {
  return controller.value?.mode.value ?? PvtModeEnum.Idle;
});
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.Pvt"
    :data="props"
  >
    <Pvt
      v-bind="props"
      :state="state"
      :height="200"
    >
      <YardTag>{{ props.tagId }}</YardTag>
      <PvtTitle class="gap-2 pb-1">
        <SolarPanelIcon class="fill-brand-muted" />
        {{ props.tooltip?.title }}
      </PvtTitle>

      <PvtMode
        :mode="modeKey"
        :state="state"
      />
      <ValueList class="gap-0 pt-1">
        <ValueListSeparator />

        <ValueListItem>
          <span class="flex items-center gap-0.5">
            <RiFireLine class="text-heating-medium size-3.5" />
          </span>
          <span class="text-foreground font-medium">
            <FieldRenderer.Heat :value="pvt?.heat.value" />
          </span>
        </ValueListItem>
        <ValueListItem>
          <span class="text-brand text-sm">{{ t("units.deltaT") }}</span>
          <span class="text-foreground font-medium">
            <FieldRenderer.Temperature :value="pvt?.deltaT.value" />
          </span>
        </ValueListItem>
        <ValueListItem>
          <span class="flex items-center gap-0.5">
            <RiDropLine class="text-brand size-3.5" />
          </span>
          <span class="text-foreground font-medium">
            <FieldRenderer.FlowRate :value="flowRate" />
          </span>
        </ValueListItem>
        <ValueListItem>
          <span class="flex items-center gap-0.5">
            <RiFlashlightLine class="text-brand size-3.5" />
          </span>
          <strong>TODO %</strong>
        </ValueListItem>
        <ValueListSeparator />
      </ValueList>
    </Pvt>
  </MimicTooltipTrigger>
</template>
