<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import {
  TooltipListItem,
  TooltipListItemSource,
  TooltipListItemTitle,
  TooltipListItemValveState,
} from "@/modules/thrapp/components/tooltip-list";
import { ExtractSensorFields } from "@/modules/thrapp/types/fields.ts";
import { MimicComponentType } from "@/modules/thrapp/types/index.ts";

const tItems = tScoped("thrapp.tooltips.items");

defineProps<ExtractSensorFields<MimicComponentType.BoilerTank>>();
</script>

<template>
  <TooltipListItem size="sm">
    <TooltipListItemTitle>
      {{ tItems("boostReturnValve") }}
      <TooltipListItemSource :source="sensors.boostReturnValve" />
    </TooltipListItemTitle>
    <TooltipListItemValveState :source="sensors.boostReturnValve" />
  </TooltipListItem>
  <TooltipListItem size="sm">
    <TooltipListItemTitle>
      {{ tItems("boostSupplyValve") }}
      <TooltipListItemSource :source="sensors.boostSupplyValve" />
    </TooltipListItemTitle>
    <TooltipListItemValveState :source="sensors.boostSupplyValve" />
  </TooltipListItem>
  <TooltipListItem size="sm">
    <TooltipListItemTitle>
      {{ tItems("supplyValve") }}
      <TooltipListItemSource :source="sensors.supplyValve" />
    </TooltipListItemTitle>
    <TooltipListItemValveState :source="sensors.supplyValve" />
  </TooltipListItem>
  <TooltipListItem size="sm">
    <TooltipListItemTitle>
      {{ tItems("dischargeValve") }}
      <TooltipListItemSource :source="sensors.dischargeValve" />
    </TooltipListItemTitle>
    <TooltipListItemValveState :source="sensors.dischargeValve" />
  </TooltipListItem>
</template>
