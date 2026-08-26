<script setup lang="ts">
import { computed, toRef } from "vue";
import { useI18n } from "vue-i18n";
import { FieldRendererProps } from ".";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));

const { t } = useI18n();

const enabled = computed(() => {
  return value.value;
});
</script>

<template>
  {{ enabled ? t("labels.enabled") : t("labels.disabled") }}
</template>
