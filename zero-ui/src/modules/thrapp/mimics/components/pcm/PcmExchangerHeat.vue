<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { RiFireLine } from "@remixicon/vue";
import { ModuleField } from "../../providers";
import SensorValue from "../../providers/SensorValue.vue";
import { FieldRenderer } from "../../renderers";

defineProps<{
  source: ModuleField<SensorComponentType.HeatTransferDevice>;
}>();
</script>

<template>
  <SensorValue
    :source="source"
    field="heat"
  >
    <div
      class="bg-foreground/5 text-foreground mx-auto flex w-fit flex-col items-center gap-0.5 text-xs leading-3"
    >
      <RiFireLine class="text-heating-medium size-3" />
      <FieldRenderer.Heat dense />
    </div>
  </SensorValue>
</template>
