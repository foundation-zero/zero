<script setup lang="ts">
import { toRef } from "vue";
import { useI18n } from "vue-i18n";
import { FieldRendererProps } from ".";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));

const { t } = useI18n();
</script>

<template>
  {{ value ? t("labels.on") : t("labels.off") }}
</template>
