<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <h1
    ref="title"
    class="tracking-ultrawide py-3 text-center text-xl font-bold uppercase"
  >
    {{ t("app.title") }}
  </h1>
</template>
