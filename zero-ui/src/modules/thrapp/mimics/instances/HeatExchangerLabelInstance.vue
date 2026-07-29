<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { ValueList, ValueListDeltaTItem, ValueListHeatPowerItem } from "../components/value-list";
import { ModuleField } from "../providers";

defineProps<
  MimicComponentInstanceProps & {
    heatExchanger: ModuleField<SensorComponentType.HeatExchanger>;
  }
>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
    height="70"
    class="w-20 py-0.5"
  >
    {{ tagId }}
    <template #value>
      <ValueList>
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
