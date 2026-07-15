<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import {
  ControlComponentType,
  ControllerStateComponentType,
  PARAMETERS_TYPES,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";
import { snakeCase } from "lodash";
import { computed, type HTMLAttributes } from "vue";
import { getTooltipContext } from "../../components/tooltip";
import {
  getControlDefinition,
  getSensorDefinition,
  injectFieldValueSource,
  ModuleField,
} from "../../mimics/providers";
import { TOOLTIPS } from "../tooltips";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  url?: boolean;
  external?: boolean;
  source?: ModuleField<
    SensorComponentType | ControlComponentType | ParametersType | ControllerStateComponentType
  >;
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

const { setTooltip, findTooltipContext } = getTooltipContext();

const tooltipContext = computed(() => (source.value ? findTooltipContext(source.value) : null));

const isParameter = computed(() => {
  if (!source.value) return false;
  const [type] = source.value;
  return PARAMETERS_TYPES.includes(type as ParametersType);
});

const openLink = () => {
  if (!tooltipContext.value) return;

  const [type, tooltip] = tooltipContext.value;

  setTooltip(tooltip, TOOLTIPS[type]);
};
</script>

<template>
  <span
    :class="
      cn('text-disabled-foreground overflow-hidden text-sm font-medium text-ellipsis', props.class)
    "
  >
    <span
      v-if="tooltipContext"
      class="cursor-pointer underline"
      @click="openLink"
    >
      <slot>
        {{ snakeCase(sourceName) }}
      </slot>
    </span>

    <RouterLink
      v-else-if="isParameter"
      class="text-brand-dull cursor-pointer underline"
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
