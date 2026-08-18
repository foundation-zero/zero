<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ENV } from "@/settings";
import { RiArrowLeftLine } from "@remixicon/vue";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const sailSystemUrl = computed(() => (ENV.VITE_SAIL_SYSTEM_URL ?? "").trim());
</script>

<template>
  <div class="bg-background relative h-svh w-screen overflow-hidden">
    <iframe
      :src="sailSystemUrl"
      class="h-full w-full border-0"
      :title="t('apps.sailSystem')"
      loading="lazy"
      referrerpolicy="strict-origin-when-cross-origin"
      allow="fullscreen"
    />

    <RouterLink
      to="/"
      class="absolute top-4 left-4 z-10"
    >
      <Button
        variant="secondary"
        class="flex items-center gap-1 rounded-full shadow-md backdrop-blur-sm"
      >
        <RiArrowLeftLine class="size-4" />
        <span>{{ t("labels.back") }}</span>
      </Button>
    </RouterLink>
  </div>
</template>
