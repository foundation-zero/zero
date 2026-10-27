<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { toRef } from "vue";
import { FieldRendererProps } from ".";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<boolean>>();

const value = getFieldValue(toRef(props, "value"));

const { t } = useI18n();
</script>

<template>
  <span v-if="value !== undefined">
    {{ value ? t("thrapp.labels.empty") : t("thrapp.labels.notEmpty") }}
  </span>
</template>
