<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { snakeCase } from "lodash";
import { computed, type HTMLAttributes } from "vue";
import {
  getControlDefinition,
  getSensorDefinition,
  injectFieldValueSource,
  ModuleField,
} from "../../mimics/providers";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  url?: boolean;
  external?: boolean;
  source?: ModuleField<SensorComponentType | ControlComponentType | ParametersType>;
}>();

const source = computed(() => props.source ?? injectFieldValueSource());

const definition = computed(() => {
  if (!source.value) return null;
  const [, moduleId, componentId] = source.value;
  return getSensorDefinition(moduleId, componentId) ?? getControlDefinition(moduleId, componentId);
});

const sourceName = computed(() =>
  definition.value?.yardTag.length ? definition.value.yardTag : source.value?.[2],
);
</script>

<template>
  <span
    :class="
      cn(
        'text-disabled-foreground overflow-hidden text-sm font-medium text-ellipsis',
        { underline: (source && !$slots['default']) || external || url, 'text-brand-dull': url },
        props.class,
      )
    "
  >
    <slot>
      <template v-if="sourceName">
        {{ snakeCase(sourceName) }}
      </template>
    </slot>
  </span>
</template>
