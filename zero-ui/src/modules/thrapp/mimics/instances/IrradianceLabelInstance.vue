<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from ".";
import { Label, LabelProps } from "../components/label";
import { ModuleField } from "../providers";
import SensorValue from "../providers/SensorValue.vue";
import { FieldRenderer } from "../renderers";

defineProps<
  MimicComponentInstanceProps &
    LabelProps & { source?: ModuleField<SensorComponentType.Irradiance>; value?: number }
>();
</script>

<template>
  <Label
    v-bind="$props"
    class="bg-inverse-muted-foreground"
  >
    {{ tagId }}
    <template #value>
      <FieldRenderer.Irradiance
        v-if="value !== undefined"
        class="text-sm font-normal"
        :value="value"
      />
      <SensorValue
        v-else-if="source"
        :source="source"
        field="irradiance"
      >
        <FieldRenderer.Irradiance class="text-sm font-normal" />
      </SensorValue>
    </template>
  </Label>
</template>
