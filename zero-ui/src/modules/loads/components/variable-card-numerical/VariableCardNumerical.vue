<script setup lang="ts">
import { computed } from "vue";
import { getLoadState } from "../../lib/utils";
import { ReferenceThresholds, VariableState, VariableType } from "../../types";
import { Card } from "../card";
import { ReferenceBox, ReferenceBoxLine, ReferenceBoxValue } from "../reference-box";
import { VariableState as VariableStateDisplay, VariableUnit } from "../variable-state";

const props = defineProps<{
  value: number;
  type: VariableType;
  thresholds?: ReferenceThresholds;
}>();

const loadState = computed(() => getLoadState(props.value, props.thresholds));
</script>

<template>
  <Card class="gap-2">
    <ReferenceBox :class="{ invisible: !thresholds?.target }">
      <ReferenceBoxValue
        :value="thresholds?.target"
        :type="type"
      />
      <ReferenceBoxLine />
    </ReferenceBox>
    <div class="flex w-full flex-col items-center">
      <VariableStateDisplay
        :type="type"
        size="xl"
        :value="value"
        :state="loadState"
      >
        <VariableUnit />
      </VariableStateDisplay>

      <header
        class="text-disabled-foreground flex items-center gap-1 pt-2 text-base font-medium text-ellipsis"
      >
        <slot />
      </header>
    </div>

    <div class="flex w-full items-center justify-between gap-14">
      <VariableStateDisplay
        class="w-9"
        :type="type"
        :value="thresholds?.alarmLow"
        :state="thresholds?.alarmLow ? VariableState.Alarm : VariableState.Unknown"
      />

      <VariableStateDisplay
        class="w-9"
        :type="type"
        :value="thresholds?.alarmHigh"
        :state="thresholds?.alarmHigh ? VariableState.Alarm : VariableState.Unknown"
      />
    </div>
  </Card>
</template>
