<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { TopNav } from "@/modules/common/components/navigation";
import { ENV } from "@/settings";
import { computed } from "vue";

const grafanaUrl = computed(() => (ENV.VITE_GRAFANA_URL ?? "").trim());
</script>

<template>
  <TopNav />

  <main class="bg-background h-svh pt-20 md:pt-24">
    <iframe
      v-if="grafanaUrl"
      :src="grafanaUrl"
      class="h-full w-full border-0"
      title="Grafana"
      loading="lazy"
      referrerpolicy="strict-origin-when-cross-origin"
    />

    <section
      v-else
      class="flex h-full items-center justify-center px-6"
    >
      <div class="bg-card border-border max-w-xl rounded-xl border p-8 text-center">
        <h1 class="text-foreground text-xl font-semibold">Grafana is not configured</h1>
        <p class="text-muted-foreground mt-3">
          Set VITE_GRAFANA_URL in your environment to enable dashboard embedding.
        </p>
        <RouterLink
          class="mt-5 inline-block"
          :to="{ name: 'splash' }"
        >
          <Button variant="secondary">Back to splash</Button>
        </RouterLink>
      </div>
    </section>
  </main>
</template>
