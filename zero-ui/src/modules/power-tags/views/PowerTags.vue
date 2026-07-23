<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useIntervalFn } from "@vueuse/core";
import { useI18n } from "vue-i18n";
import { usePowerTagsStore } from "../stores/power-tags";

const POLL_INTERVAL_MS = 10_000;

const { t } = useI18n();
const store = usePowerTagsStore();

const formatValue = (value: number | null, unit: string | null, fractionDigits = 1): string => {
  if (value === null || value === undefined) {
    return "—";
  }
  const formatted = new Intl.NumberFormat("en-US", {
    maximumFractionDigits: fractionDigits,
  }).format(value);
  return unit ? `${formatted} ${unit}` : formatted;
};

const rowTestId = (topic: string): string => `power-tags-row-${topic.replace(/\//g, "-")}`;

useIntervalFn(() => store.refresh(), POLL_INTERVAL_MS);
</script>

<template>
  <article class="flex flex-col gap-4">
    <div
      v-if="store.fetching && !store.sortedPanels.length"
      class="text-muted-foreground text-sm"
    >
      {{ t("powerTags.loading") }}
    </div>
    <div
      v-else-if="store.error"
      class="text-destructive text-sm"
    >
      {{ t("powerTags.error") }}
    </div>
    <template v-else-if="store.sortedPanels.length">
      <div class="flex items-center justify-end">
        <Button
          variant="outline"
          size="sm"
          data-testid="power-tags-toggle"
          :aria-expanded="store.showAll"
          @click="store.showAll = !store.showAll"
        >
          {{ store.showAll ? t("powerTags.toggle.showLess") : t("powerTags.toggle.showAll") }}
        </Button>
      </div>
      <div
        v-if="store.allReadingsNull"
        class="text-sm text-amber-600 dark:text-amber-400"
        data-testid="power-tags-offline-notice"
      >
        {{ t("powerTags.offlineNotice") }}
      </div>
      <div
        :data-testid="`power-tags-panel-${store.activePanel}`"
        class="bg-background border-border-subtle mx-auto w-full rounded-md border"
        :class="{ 'max-w-6xl': !store.showAll }"
      >
        <Table :data-testid="`power-tags-table-${store.activePanel}`">
          <TableHeader>
            <TableRow>
              <TableHead data-testid="power-tags-header-component">
                {{ t("powerTags.columns.component") }}
              </TableHead>
              <TableHead
                data-testid="power-tags-header-consumer"
                :class="{ 'w-full': !store.showAll }"
              >
                {{ t("powerTags.columns.consumer") }}
              </TableHead>
              <TableHead
                v-for="col in store.visibleColumns"
                :key="col.key"
                class="text-right whitespace-nowrap"
                :data-testid="`power-tags-header-${col.key}`"
              >
                {{ t(`powerTags.columns.${col.key}`) }}
                <span v-if="store.unitByName[col.key]"> ({{ store.unitByName[col.key] }}) </span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow
              v-for="tag in store.activePowerTags"
              :key="tag.topic"
              :data-testid="rowTestId(tag.topic)"
            >
              <TableCell>{{ tag.metadata.component ?? "—" }}</TableCell>
              <TableCell :class="store.showAll ? 'max-w-[24ch] truncate' : 'truncate'">
                {{ tag.metadata.consumer ?? "—" }}
              </TableCell>
              <TableCell
                v-for="col in store.visibleColumns"
                :key="col.key"
                class="text-right whitespace-nowrap tabular-nums"
                :data-testid="`power-tags-value-${col.key}`"
              >
                {{
                  formatValue(
                    tag.values[col.key],
                    store.unitByName[col.key] ?? null,
                    col.key.startsWith("powerFactor") ? 2 : 1,
                  )
                }}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </template>
    <div
      v-else
      class="text-muted-foreground text-sm"
    >
      {{ t("powerTags.loading") }}
    </div>
  </article>
</template>
