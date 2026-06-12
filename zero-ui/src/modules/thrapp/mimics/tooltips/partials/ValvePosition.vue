<script setup lang="ts">
import { formatInt, ratioAsPercentage } from "@/modules/common/lib/utils";
import {
  TooltipListItem,
  TooltipListItemNumber,
  TooltipListItemTitle,
} from "@/modules/thrapp/components/tooltip-list";
import { SensorComponentType } from "@/modules/thrs/types";
import { computed } from "vue";
import { useTranslations } from "..";
import { getMimicDataProvider, ModuleField } from "../../providers";

const { items, units } = useTranslations();

const props = defineProps<{ valve: ModuleField<SensorComponentType.Valve> }>();

const { getSensorValue } = getMimicDataProvider();

const valve = getSensorValue(props.valve);
const position = computed(() => valve.value?.positionRel.value);
const positionRelative = ratioAsPercentage(position);
const positionAbsolute = computed(() =>
  position.value === undefined ? undefined : 360 * position.value,
);
</script>

<template>
  <TooltipListItem>
    <TooltipListItemTitle>{{ items("relativePosition") }}</TooltipListItemTitle>
    <TooltipListItemNumber
      :value="positionRelative"
      :unit="units('percent')"
      :format="formatInt"
      dense
    />
  </TooltipListItem>
  <TooltipListItem>
    <TooltipListItemTitle>{{ items("absolutePosition") }}</TooltipListItemTitle>
    <TooltipListItemNumber
      :value="positionAbsolute"
      :unit="units('degrees')"
      :format="formatInt"
      dense
    />
  </TooltipListItem>
</template>
