<script setup lang="ts">
import { cn, isStampedWithSource } from "@/modules/common/lib/utils";
import { THRS_YARDTAG_PREFIX_REGEX } from "@/modules/thrapp/lib/consts";
import { snakeCase } from "lodash";
import { computed, type HTMLAttributes } from "vue";
import { FieldRenderer } from ".";
import { getTooltipContext } from "../../components/tooltip";
import {
  getDefinition,
  getFieldValueData,
  injectFieldValueSource,
  isParameterField,
  ModuleField,
} from "../../mimics/providers";
import { useTranslations } from "../tooltips";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  source?: ModuleField;
  apiOnly?: boolean;
  noLink?: boolean;
}>();

const { sources } = useTranslations();

const source = computed(() => props.source ?? injectFieldValueSource());
const sourceData = getFieldValueData();

const definition = computed(() => {
  if (!source.value) return null;

  return getDefinition(source.value);
});

const backendSource = computed(() => {
  const sourcedataTyped = sourceData.value;

  if (!isStampedWithSource(sourcedataTyped)) return null;

  if (!sourcedataTyped.source) return "";

  if (["unknown", "calculated"].includes(sourcedataTyped.source))
    return sources(sourcedataTyped.source);

  return sourcedataTyped.source.replace(THRS_YARDTAG_PREFIX_REGEX, "");
});

const sourceName = computed(() => {
  if (backendSource.value || (props.apiOnly && !props.source)) {
    return backendSource.value ?? "";
  } else if (tooltipContext.value?.tooltip?.yardTag) return tooltipContext.value.tooltip.yardTag;
  else if (!definition.value || !("yardTag" in definition.value))
    return snakeCase(source.value?.[2]);

  return definition.value.yardTag ?? source.value?.[2];
});

const { findTooltipContext } = getTooltipContext();

const tooltipContext = computed(() => {
  if (backendSource.value) {
    return findTooltipContext(backendSource.value)[0];
  } else if (source.value) {
    return findTooltipContext(source.value)[0];
  }
  return null;
});
const isParameter = computed(() => isParameterField(source.value));
const showLink = computed(() => !props.noLink && tooltipContext.value);
</script>

<template>
  <span
    :class="
      cn('text-disabled-foreground overflow-hidden text-sm font-medium text-ellipsis', props.class)
    "
  >
    <RouterLink
      v-if="tooltipContext && showLink"
      class="cursor-pointer underline"
      :to="{
        query: {
          ...$route.query,
          tooltip: tooltipContext.registerField,
          type: tooltipContext.type,
        },
      }"
    >
      <slot>
        {{ sourceName }}
      </slot>
    </RouterLink>

    <RouterLink
      v-else-if="isParameter"
      class="text-brand-dull cursor-pointer underline"
      target="_blank"
      rel="noopener noreferrer"
      :to="{
        name: 'thrs/control',
        params: {
          module: source?.[1],
        },
        query: { ...$route.query, parameter: source?.[2] },
      }"
    >
      <slot>
        {{ snakeCase(sourceName) }}
      </slot>
    </RouterLink>

    <FieldRenderer.Placeholder v-else-if="sourceName === 'placeholder'" />
    <slot v-else-if="sourceName">
      {{ sourceName }}
    </slot>

    <slot v-else />
  </span>
</template>
