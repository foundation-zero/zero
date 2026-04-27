<script setup lang="ts">
import AlertBox from "@/modules/thrs/components/AlertBox.vue";
import { DEFINITIONS } from "@/modules/thrs/lib/consts";
import { useThrsHistory } from "@/modules/thrs/stores/history";
import { computed, toRefs } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const MODULES = Object.keys(DEFINITIONS) as Array<keyof typeof DEFINITIONS>;
const { data } = toRefs(useThrsHistory());

const environment = computed(() => data.value?.environment ?? "simulation");

const moduleStatuses = computed(() =>
  MODULES.map((moduleName) => ({
    moduleName,
    advisoryControlEnabled: data.value?.modules[moduleName]?.advisoryControlEnabled ?? null,
  })),
);
</script>

<template>
  <header class="mb-4 text-3xl capitalize">{{ t("thrs.views.overview.title") }}</header>

  <section class="mb-6 rounded-lg border p-4">
    <h2 class="text-sm font-medium uppercase">{{ t("thrs.views.overview.environment") }}</h2>
    <p class="mt-2 text-lg font-semibold capitalize">{{ environment }}</p>
  </section>

  <section
    v-if="environment === 'boat'"
    class="rounded-lg border p-4"
  >
    <h2 class="mb-3 text-sm font-medium uppercase">
      {{ t("thrs.views.overview.moduleAdvisoryControl") }}
    </h2>
    <ul class="space-y-2">
      <li
        v-for="status in moduleStatuses"
        :key="status.moduleName"
        class="flex items-center justify-between rounded-md border px-3 py-2"
      >
        <span class="capitalize">{{ status.moduleName }}</span>
        <span
          v-if="status.advisoryControlEnabled === true"
          class="text-constructive"
        >
          {{ t("thrs.views.overview.advisoryEnabled") }}
        </span>
        <span
          v-else-if="status.advisoryControlEnabled === false"
          class="text-warning"
        >
          {{ t("thrs.views.overview.advisoryDisabled") }}
        </span>
        <span
          v-else
          class="text-destructive"
        >
          {{ t("thrs.views.overview.advisoryNotReceived") }}
        </span>
      </li>
    </ul>
  </section>

  <AlertBox v-else>{{ t("thrs.views.overview.simulationIndicator") }}</AlertBox>
</template>
