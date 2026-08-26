<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { Label, LabelProps } from "../components/label";
import { FieldRenderer } from "../renderers";

defineProps<MimicComponentInstanceProps & LabelProps>();
</script>

<template>
  <Label
    v-bind="$props"
    class="bg-inverse-muted-foreground"
  >
    {{ tagId }}
    <template #value>
      <FieldRenderer.Irradiance
        class="text-sm font-normal"
        :value="523"
      />
    </template>
  </Label>
</template>
