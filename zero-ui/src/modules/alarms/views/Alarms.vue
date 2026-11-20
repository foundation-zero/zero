<script setup lang="ts">
import { useIntervalFn } from "@vueuse/core";
import { useI18n } from "vue-i18n";
import { AlarmTable } from "../components/alarm-table";
import { POLL_INTERVAL_MS } from "../lib/consts";
import { useAlarmsStore } from "../stores/alarms";

const { t } = useI18n();
const store = useAlarmsStore();

useIntervalFn(() => store.refresh(), POLL_INTERVAL_MS);
</script>

<template>
  <article class="mx-auto flex w-full max-w-7xl flex-col gap-6">
    <!-- After a failed refresh the last list may be outdated, so it is not shown. -->
    <div
      v-if="store.error"
      class="border-destructive bg-destructive/10 rounded-md border px-4 py-3 text-sm"
      data-testid="alarms-error"
    >
      {{ t("alarms.error") }}
    </div>
    <div
      v-else-if="!store.loaded"
      class="text-muted-foreground text-sm"
    >
      {{ t("alarms.loading") }}
    </div>
    <div
      v-else-if="store.offline"
      class="border-warning bg-warning/10 rounded-md border px-4 py-3 text-sm"
      data-testid="alarms-offline"
    >
      {{ t("alarms.offline") }}
    </div>
    <template v-else>
      <section
        class="flex flex-col gap-2"
        data-testid="alarms-active"
      >
        <h2 class="text-lg font-medium">
          {{ t("alarms.sections.active", { count: store.activeAlarms.length }) }}
        </h2>
        <AlarmTable
          v-if="store.activeAlarms.length"
          :alarms="store.activeAlarms"
        />
        <p
          v-else
          class="text-muted-foreground text-sm"
        >
          {{ t("alarms.empty.active") }}
        </p>
      </section>
      <section
        class="flex flex-col gap-2"
        data-testid="alarms-ended"
      >
        <h2 class="text-lg font-medium">
          {{ t("alarms.sections.ended", { count: store.endedAlarms.length }) }}
        </h2>
        <p class="text-muted-foreground text-sm">
          {{ t("alarms.endedNotice", { minutes: store.windowMinutes }) }}
        </p>
        <AlarmTable
          v-if="store.endedAlarms.length"
          :alarms="store.endedAlarms"
          ended
        />
      </section>
    </template>
  </article>
</template>
