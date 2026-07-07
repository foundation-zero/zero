<script setup lang="ts">
import { ParametersType } from "@/modules/thrs/types";
import { computed, toRef } from "vue";
import { useI18n } from "vue-i18n";
import { FieldRendererProps } from ".";
import { getFieldValue, injectFieldValueSource } from "../providers";

const props = defineProps<FieldRendererProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));
const source = injectFieldValueSource();

const { t } = useI18n();

const enabled = computed(() => {
  if (source?.[0] === ParametersType.Disabled) {
    return !value.value;
  } else {
    return value.value;
  }
});
</script>

<template>
  {{ enabled ? t("labels.enabled") : t("labels.disabled") }}
</template>
