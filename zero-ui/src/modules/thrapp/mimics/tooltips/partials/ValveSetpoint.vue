<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { VALVE_OPEN_THRESHOLD } from "@/modules/thrapp/utils/consts";
import { ControlComponentType } from "@/modules/thrs/types";
import { computed } from "vue";
import { useTranslations } from "..";
import { getMimicDataProvider, ModuleField } from "../../providers";

const { items, labels } = useTranslations();

const props = defineProps<{ valve: ModuleField<ControlComponentType.Valve> }>();

const { getControlValue } = getMimicDataProvider();

const valve = getControlValue(props.valve);
const isClosed = computed(() => (valve.value?.setpoint.value ?? 0) < VALVE_OPEN_THRESHOLD);
</script>

<template>
  <TooltipListItem>
    <TooltipListItemTitle>
      {{ items("setpoint") }}
      <slot />
    </TooltipListItemTitle>
    <TooltipListItemValue>{{ isClosed ? labels("closed") : labels("open") }}</TooltipListItemValue>
  </TooltipListItem>
</template>
