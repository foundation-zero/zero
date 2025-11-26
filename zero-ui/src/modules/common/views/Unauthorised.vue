<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <article class="flex h-full flex-col items-center justify-center text-center">
    <h1 class="text-6xl font-bold">{{ t("views.unauthorised.title") }}</h1>
    <p class="mt-4 text-2xl font-medium">{{ t("views.unauthorised.description") }}</p>
  </article>
</template>
