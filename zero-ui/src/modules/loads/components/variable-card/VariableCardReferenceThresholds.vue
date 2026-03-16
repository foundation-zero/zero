<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { getContext } from ".";
import { VariableState } from "../../types";
import { VariableState as VariableStateDisplay } from "../variable-state";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const { thresholds, type, value } = getContext();
</script>

<template>
  <div :class="cn('flex w-full items-center justify-around', props.class)">
    <VariableStateDisplay
      class="w-9"
      size="sm"
      :type="type"
      :value="thresholds?.alarmLow"
      :state="
        thresholds?.alarmLow && value != null && value < thresholds.alarmLow
          ? VariableState.Alarm
          : VariableState.Unknown
      "
    />

    <slot />

    <VariableStateDisplay
      class="w-9"
      size="sm"
      :type="type"
      :value="thresholds?.alarmHigh"
      :state="
        thresholds?.alarmHigh && value != null && value >= thresholds.alarmHigh
          ? VariableState.Alarm
          : VariableState.Unknown
      "
    />
  </div>
</template>
