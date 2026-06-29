<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import {
  ControlComponentType,
  ControllerStateComponentType,
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

const openLink = () => {
  const result = tooltipContext.value;
  if (!result) return;

  const [type, tooltip] = result;

  setTooltip(tooltip, TOOLTIPS[type]);
};
</script>

<template>
  <span
    :class="
      cn(
        'text-disabled-foreground overflow-hidden text-sm font-medium text-ellipsis',
        {
          'text-brand-dull': url,
          'cursor-pointer underline': !!tooltipContext && !$slots['default'],
        },
        props.class,
      )
    "
    @click="openLink"
  >
    <slot>
      <template v-if="sourceName">
        {{ snakeCase(sourceName) }}
      </template>
    </slot>
  </span>
</template>
