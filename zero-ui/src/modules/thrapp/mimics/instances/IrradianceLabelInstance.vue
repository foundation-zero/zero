<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";
import { FieldRenderer } from "../renderers";

defineProps<MimicComponentInstanceProps & {}>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
    class="bg-transparent"
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
