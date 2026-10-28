<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { toRef } from "vue";
import { FieldRendererProps } from ".";
import { VALVE_OPEN_THRESHOLD } from "../../utils/consts";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<number>>();

const value = getFieldValue(toRef(props, "value"));

const { t } = useI18n();
</script>

<template>
  {{ (value ?? 0) < VALVE_OPEN_THRESHOLD ? t("thrapp.labels.closed") : t("thrapp.labels.open") }}
</template>
