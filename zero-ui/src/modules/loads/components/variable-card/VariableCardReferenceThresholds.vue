<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { getContext } from ".";
import { VariableState } from "../../types";
import { VariableState as VariableStateDisplay } from "../variable-state";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const { thresholds, type } = getContext();
</script>

<template>
  <div :class="cn('flex w-full items-center justify-between gap-14', props.class)">
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
</template>
