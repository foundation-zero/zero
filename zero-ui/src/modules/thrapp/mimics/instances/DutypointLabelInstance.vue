<script setup lang="ts">
import { formatNumber } from "@/modules/common/lib/utils";
import { SensorComponentType } from "@/modules/thrs/types";
import { Label } from "../components/label/index.ts";
import { ModuleField } from "../providers/index.ts";
import SensorValue from "../providers/SensorValue.vue";
import { FieldRenderer } from "../renderers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";

defineProps<MimicComponentInstanceProps & { pump: ModuleField<SensorComponentType.Pump> }>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
  >
    {{ tagId }}
    <template #value>
      <SensorValue
        :source="pump"
        field="flow"
      >
        <FieldRenderer.Percentage :format="formatNumber.int" />
      </SensorValue>
    </template>
  </Label>
</template>
