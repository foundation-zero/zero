<script setup lang="ts">
import { ZiHeatBatteryFull } from "@/modules/common/components/icons";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { Pcm, PcmLayout, PcmTitle } from "../components/pcm";
import PcmContent from "../components/pcm/PcmContent.vue";
import {
  ValueList,
  ValueListHeatPowerItem,
  ValueListItem,
  ValueListSeparator,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import ControllerStateValue from "../providers/ControllerStateValue.vue";
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
          field="chargeStatus"
        >
          <FieldRenderer.ChargeState />
        </ControllerStateValue>
        <ValueList class="gap-0 text-base font-medium">
          <ValueListSeparator class="my-0.5" />
          <ValueListHeatPowerItem :source="sensors.heatTransfer" />
          <ValueListItem>
            <ZiHeatBatteryFull
              class="size-3.5"
              icon-class="fill-muted-foreground "
            />
            <ControllerStateValue
              :source="controllerState.chargeController"
              field="energy"
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
