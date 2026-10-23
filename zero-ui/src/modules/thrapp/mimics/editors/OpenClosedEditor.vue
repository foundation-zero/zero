<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { cn } from "@/modules/common/lib/utils.ts";
import { computed, toRef } from "vue";
import { FieldEditorProps } from ".";
import { VALVE_OPEN_THRESHOLD } from "../../utils/consts.ts";
import { getFieldValue } from "../providers";
import EditableField from "./EditableField.vue";

const props = defineProps<FieldEditorProps<number>>();

const value = getFieldValue(toRef(props, "value"));
const state = computed({
  get: () => value.value != undefined && value.value > VALVE_OPEN_THRESHOLD,
  set: (newState: boolean) => {
    value.value = newState ? 1 : 0;
  },
});
</script>

<template>
  <span :class="cn('flex items-center gap-1', props.class)">
    <EditableField>
      <slot />
      <template #editor>
        <slot />
        <Switch v-model="state" />
      </template>
    </EditableField>
  </span>
</template>
