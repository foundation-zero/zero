<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { SensorComponentType } from "@/modules/thrs/types";
import { computed, type HTMLAttributes } from "vue";
import { getSensorDefinition, ModuleField } from "../../mimics/providers";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  url?: boolean;
  external?: boolean;
  source?: ModuleField<SensorComponentType>;
}>();

const definition = computed(() => {
  if (!props.source) return null;
  const [, moduleId, componentId] = props.source;
  return getSensorDefinition(moduleId, componentId);
});
</script>

<template>
  <span
    :class="
      cn(
        'text-disabled-foreground overflow-hidden text-sm font-medium text-ellipsis',
        { underline: source || external || url, 'text-brand-dull': url },
        props.class,
      )
    "
  >
    <slot>
      <template v-if="definition?.yardTag">
        {{ definition.yardTag }}
      </template>
    </slot>
  </span>
</template>
