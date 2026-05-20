<script setup lang="ts">
import { MimicComponentInstanceProps, useRandomizedNumber } from ".";
import { Label } from "../components/label";
import { ValueList, ValueListDeltaTItem, ValueListHeatPowerItem } from "../components/value-list";

defineProps<MimicComponentInstanceProps>();

const deltaTRaw = useRandomizedNumber(-90, 90);
const powerRaw = useRandomizedNumber(5, 30);
</script>

<template>
  <Label
    :x="x"
    :y="y"
    class="w-20"
  >
    {{ tagId }}
    <template #value>
      <ValueList>
        <ValueListDeltaTItem
          class="text-sm"
          :value="deltaTRaw"
        />
        <ValueListHeatPowerItem
          class="text-sm"
          :value="powerRaw"
        />
      </ValueList>
    </template>
  </Label>
</template>
