<script setup lang="ts">
import { ZiHeatBatteryFull } from "@/modules/common/components/icons";
import { isDefined } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { Pcm, PcmExchangerHeat, PcmLayout, PcmTitle } from "../components/pcm";
import PcmContent from "../components/pcm/PcmContent.vue";
import {
  ValueList,
  ValueListHeatPowerItem,
  ValueListItem,
  ValueListSeparator,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider } from "../providers";
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
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);

const { getSensorValue } = getMimicDataProvider();
const heatTransfer = getSensorValue(props.sensors.heatTransfer);
const freshwaterHeatTransfer =
  props.sensors.freshwaterHeatTransfer && getSensorValue(props.sensors.freshwaterHeatTransfer);

const totalHeat = computed(() => {
  const heat = heatTransfer.value?.heat.value;
  const freshwaterHeat = freshwaterHeatTransfer?.value?.heat.value;
  return isDefined(heat) || isDefined(freshwaterHeat)
    ? (heat ?? 0) + (freshwaterHeat ?? 0)
    : undefined;
});
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <Pcm
      v-bind="forwardedProps"
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
          <ValueListHeatPowerItem
            :source="sensors.heatTransfer"
            :value="totalHeat"
          />
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
      <template
        v-if="sensors.freshwaterHeatTransfer"
        #left-exchanger
      >
        <PcmExchangerHeat :source="sensors.heatTransfer" />
      </template>
      <template
        v-if="sensors.freshwaterHeatTransfer"
        #right-exchanger
      >
        <PcmExchangerHeat :source="sensors.freshwaterHeatTransfer" />
      </template>
    </Pcm>
    <slot />
  </MimicTooltipTrigger>
</template>
