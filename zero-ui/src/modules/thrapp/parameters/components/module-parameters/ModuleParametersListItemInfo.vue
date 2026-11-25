<script setup lang="ts">
import { SimpleInfoTooltip } from "@/modules/common/components/info-tooltip";
import { getParameterDefinition, ModuleField } from "@/modules/thrapp/mimics/providers";
import { useTranslations } from "@/modules/thrapp/mimics/tooltips";
import { ParametersType } from "@/modules/thrapp/types/thrs";
import { computed } from "vue";

const props = defineProps<{ source: ModuleField<ParametersType> }>();

const { descriptions } = useTranslations();

// A description in en.json overrides the one in the AsyncAPI Spec.
const description = computed(() => {
  const [, module, field] = props.source;
  return descriptions.exists(field)
    ? descriptions(field)
    : getParameterDefinition(module, field)?.description;
});
</script>

<template>
  <SimpleInfoTooltip v-if="description">{{ description }}</SimpleInfoTooltip>
</template>
