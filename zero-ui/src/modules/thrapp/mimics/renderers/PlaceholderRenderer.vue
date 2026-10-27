<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <span :aria-label="t('thrapp.labels.placeholder')">⚠️</span>
</template>
