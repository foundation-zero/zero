<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { ModuleField } from "../providers";
import SensorValue from "../providers/SensorValue.vue";
import { FieldRenderer } from "../renderers";

defineProps<MimicComponentInstanceProps & { flow: ModuleField<SensorComponentType.Flow> }>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
  >
    {{ tagId }}
    <template #value>
      <SensorValue
        :source="flow"
        field="flow"
      >
        <FieldRenderer.FlowRate />
      </SensorValue>
    </template>
  </Label>
</template>
