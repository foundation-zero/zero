<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useActiveAlarmCount } from "./active-alarms-badge.utils";

const { t } = useI18n();
const count = useActiveAlarmCount();
</script>

<template>
  <!-- Not the shared Badge: its destructive variant has dark text, hard to read in dark mode. -->
  <span
    v-if="count"
    class="bg-destructive ring-background flex h-7 min-w-7 items-center justify-center rounded-full px-2 text-sm font-semibold text-white tabular-nums ring-2"
    data-testid="active-alarms-badge"
  >
    <span aria-hidden="true">{{ count }}</span>
    <span class="sr-only">{{ t("alarms.activeCount", { count }, count) }}</span>
  </span>
</template>
