<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { RiArrowDownLine } from "@remixicon/vue";
import { MimicComponentInstanceProps } from "..";
import { TooltipComponentContext } from "../../../components/tooltip";
import { MimicComponentType } from "../../../types";
import { CircuitBox, CircuitBoxTitle } from "../../components/circuit-box";
import { ModeBadge, ModeBadgeMode, ModeBadges, ModeBadgeSize } from "../../components/mode-badge";
import {
  ValueList,
  ValueListFlowItem,
  ValueListHeader,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../../components/value-list";
import { getMimicDataProvider } from "../../providers";

defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.ConnectingCircuit> & { noContent?: boolean }
>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();

const t = tScoped("labels");
</script>

<template>
  <CircuitBox :state="state">
    <CircuitBoxTitle class="mb-1">
      <slot>
        {{ tooltip?.title }}
      </slot>
    </CircuitBoxTitle>
    <slot
      v-if="!noContent"
      name="content"
    >
      <ModeBadges
        v-if="custom.modeModule"
        :module="custom.modeModule"
        :size="ModeBadgeSize.Circuit"
      />
      <ModeBadge
        v-else-if="!custom.consumingCircuit"
        :mode="ModeBadgeMode.Consuming"
        label="Consuming"
        :size="ModeBadgeSize.Circuit"
      />
      <ValueList class="mt-1 gap-0">
        <ValueListSeparator />
        <ValueListHeader>
          <slot name="from">
            <slot name="fromIcon">
              <RiArrowDownLine class="text-muted-foreground size-3" />
            </slot>
            {{ t("from") }}
          </slot>
        </ValueListHeader>
        <ValueListFlowItem :source="sensors.flowIn" />
        <ValueListTemperatureItem :source="sensors.tIn" />
        <ValueListSeparator />
        <ValueListHeader>
          <slot name="to">
            <slot name="toIcon">
              <RiArrowDownLine class="text-muted-foreground size-3" />
            </slot>
            {{ t("to") }}
          </slot>
        </ValueListHeader>
        <ValueListFlowItem :source="sensors.flowOut" />
        <ValueListTemperatureItem :source="sensors.tOut" />
        <ValueListSeparator />
      </ValueList>
    </slot>
  </CircuitBox>
</template>
