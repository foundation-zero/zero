<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from ".";
import type { LabelProps } from "../components/label";
import { Label } from "../components/label";
import { ValueList, ValueListDeltaTItem, ValueListHeatPowerItem } from "../components/value-list";
import { ModuleField } from "../providers";

defineProps<
  MimicComponentInstanceProps &
    LabelProps & {
      heatExchanger: ModuleField<SensorComponentType.HeatExchanger>;
    }
>();
</script>

<template>
  <Label
    v-bind="$props"
    height="70"
    class="py-0.5"
  >
    {{ tagId }}
    <template #value>
      <ValueList class="gap-0">
        <ValueListDeltaTItem
          class="text-sm"
          :source="heatExchanger"
        />
        <ValueListHeatPowerItem
          class="text-sm"
          :source="heatExchanger"
        />
      </ValueList>
    </template>
  </Label>
</template>
