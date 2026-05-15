<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { TopNav } from "@/modules/common/components/navigation";
import { ENV } from "@/settings";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const grafanaUrl = computed(() => (ENV.VITE_GRAFANA_URL ?? "").trim());
</script>

<template>
  <TopNav />

  <main class="bg-background h-svh pt-20 md:pt-24">
    <iframe
      v-if="grafanaUrl"
      :src="grafanaUrl"
      class="h-full w-full border-0"
      :title="t('apps.grafana')"
      loading="lazy"
      referrerpolicy="strict-origin-when-cross-origin"
    />

    <section
      v-else
      class="flex h-full items-center justify-center px-6"
    >
      <div class="bg-card border-border max-w-xl rounded-xl border p-8 text-center">
        <h1 class="text-foreground text-xl font-semibold">
          {{ t("views.grafana.notConfigured") }}
        </h1>
        <p class="text-muted-foreground mt-3">
          {{ t("views.grafana.configureEnv") }}
        </p>
        <RouterLink
          class="mt-5 inline-block"
          :to="{ name: 'splash' }"
        >
          <Button variant="secondary">{{ t("views.grafana.backToSplash") }}</Button>
        </RouterLink>
      </div>
    </section>
  </main>
</template>
