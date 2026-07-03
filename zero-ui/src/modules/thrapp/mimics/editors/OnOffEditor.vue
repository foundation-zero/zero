<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { toRef } from "vue";
import { getFieldValue } from "../providers/index.ts";
import EditableField from "./EditableField.vue";
import { FieldEditorProps } from "./index.ts";

const props = defineProps<FieldEditorProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));
</script>

<template>
  <span class="flex items-center gap-1">
    <EditableField>
      <slot />
      <template #editor>
        <slot />
        <Switch v-model="value" />
      </template>
    </EditableField>
  </span>
</template>
