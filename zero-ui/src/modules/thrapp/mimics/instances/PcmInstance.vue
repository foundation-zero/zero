<script setup lang="ts">
import { ZiHeatBatteryFull } from "@/modules/common/components/icons";
import { RiFireLine } from "@remixicon/vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { Pcm, PcmLayout, PcmTitle } from "../components/pcm";
import PcmContent from "../components/pcm/PcmContent.vue";
import { ValueList, ValueListItem, ValueListSeparator } from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import ControllerStateValue from "../providers/ControllerStateValue.vue";
import SensorValue from "../providers/SensorValue.vue";
import { FieldRenderer } from "../renderers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.Pcm> & {
        layout?: PcmLayout;
      }
  >(),
  {
    layout: PcmLayout.LeftTopBottom,
  },
);
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.Pcm"
    :data="props"
  >
    <Pcm
      v-bind="props"
      :layout="layout"
    >
      <div class="my-0 shrink grow-0">
        <YardTag>{{ tooltip?.yardTag }}</YardTag>
      </div>
      <PcmTitle>{{ tooltip?.title }}</PcmTitle>
      <PcmContent>
        <ControllerStateValue
          :source="controllerState.chargeController"
          field="chargingState"
        >
          <FieldRenderer.ChargingMode />
        </ControllerStateValue>
        <ControllerStateValue
          :source="controllerState.chargeController"
          field="charge"
        >
          <FieldRenderer.ChargeState />
        </ControllerStateValue>
        <ValueList class="gap-0 text-base font-medium">
          <ValueListSeparator class="my-0.5" />
          <ValueListItem>
            <RiFireLine class="text-heating-medium size-3.5" />
            <SensorValue
              :source="sensors.heatExchanger"
              field="heat"
            >
              <FieldRenderer.Auto />
            </SensorValue>
          </ValueListItem>
          <ValueListItem>
            <ZiHeatBatteryFull
              class="size-3.5"
              icon-class="fill-muted-foreground "
            />
            <ControllerStateValue
              :source="controllerState.chargeController"
              field="charge"
            >
              <FieldRenderer.Auto />
            </ControllerStateValue>
          </ValueListItem>
          <ValueListSeparator class="my-0.5" />
        </ValueList>
      </PcmContent>
    </Pcm>
    <slot />
  </MimicTooltipTrigger>
</template>
