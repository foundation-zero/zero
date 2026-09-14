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
        <SensorValue
          :source="source"
          field="deltaT"
        >
          <FieldRenderer.ChargingMode />
        </SensorValue>
        <SensorValue
          :source="source"
          field="charge"
        >
          <FieldRenderer.ChargeState />
        </SensorValue>
        <ValueList class="gap-0 text-base font-medium">
          <ValueListSeparator class="my-0.5" />
          <ValueListItem>
            <RiFireLine class="text-heating-medium size-3.5" />
            <SensorValue
              :source="source"
              field="deltaT"
            >
              <FieldRenderer.Auto />
            </SensorValue>
          </ValueListItem>
          <ValueListItem>
            <ZiHeatBatteryFull
              class="size-3.5"
              icon-class="fill-muted-foreground "
            />
            <SensorValue
              :source="source"
              field="charge"
            >
              <FieldRenderer.Auto />
            </SensorValue>
          </ValueListItem>
          <ValueListSeparator class="my-0.5" />
        </ValueList>
      </PcmContent>
    </Pcm>
    <slot />
  </MimicTooltipTrigger>
</template>
