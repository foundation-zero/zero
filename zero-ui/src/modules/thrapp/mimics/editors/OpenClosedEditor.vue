<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { computed, toRef } from "vue";
import { VALVE_OPEN_THRESHOLD } from "../../utils/consts.ts";
import { getFieldValue } from "../providers/index.ts";
import EditableField from "./EditableField.vue";
import { FieldEditorProps } from "./index.ts";

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
  <span class="flex items-center gap-1">
    <EditableField>
      <slot />
      <template #editor>
        <slot />
        <Switch v-model="state" />
      </template>
    </EditableField>
  </span>
</template>
