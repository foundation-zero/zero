<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { snakeCase } from "lodash";
import { computed, type HTMLAttributes } from "vue";
import { getTooltipContext } from "../../components/tooltip";
import {
  getDefinition,
  injectFieldValueSource,
  isParameterField,
  ModuleField,
} from "../../mimics/providers";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  url?: boolean;
  external?: boolean;
  source?: ModuleField;
}>();

const source = computed(() => props.source ?? injectFieldValueSource());

const definition = computed(() => {
  if (!source.value) return null;

  return getDefinition(source.value);
});

const sourceName = computed(() => {
  if (!definition.value || !("yardTag" in definition.value)) return source.value?.[2];

  return definition.value.yardTag ?? source.value?.[2];
});

const { findTooltipContext } = getTooltipContext();

const tooltipContext = computed(() => (source.value ? findTooltipContext(source.value) : null));
const isParameter = computed(() => isParameterField(source.value));
</script>

<template>
  <span
    :class="
      cn('text-disabled-foreground overflow-hidden text-sm font-medium text-ellipsis', props.class)
    "
  >
    <RouterLink
      v-if="tooltipContext"
      class="cursor-pointer underline"
      :to="{
        query: { tooltip: source?.join('.') },
      }"
    >
      <slot>
        {{ snakeCase(sourceName) }}
      </slot>
    </RouterLink>

    <RouterLink
      v-else-if="isParameter"
      class="text-brand-dull cursor-pointer underline"
      target="_blank"
      :to="{
        name: 'thrs/control',
        params: {
          module: source?.[1],
        },
        query: { parameter: source?.[2] },
      }"
    >
      <slot>
        {{ snakeCase(sourceName) }}
      </slot>
    </RouterLink>

    <slot v-else-if="sourceName">
      {{ snakeCase(sourceName) }}
    </slot>

    <slot v-else />
  </span>
</template>
