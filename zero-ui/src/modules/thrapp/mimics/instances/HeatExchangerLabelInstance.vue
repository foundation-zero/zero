<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { ValueList, ValueListDeltaTItem, ValueListHeatPowerItem } from "../components/value-list";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & {
    heatExchanger: ModuleField<SensorComponentType.HeatExchanger>;
  }
>();

const { getSensorValue } = getMimicDataProvider();
const heatExchanger = getSensorValue(props.heatExchanger);
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
          :value="heatExchanger?.deltaT?.value"
        />
        <ValueListHeatPowerItem
          class="text-sm"
          :value="heatExchanger?.heat?.value"
        />
      </ValueList>
    </template>
  </Label>
</template>
