<script setup lang="ts">
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { computed, onMounted, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import { LOADS_CONTEXT } from "../graphql/client";
import { VARIABLE_ACTUALS, VARIABLE_DEFINITIONS } from "../graphql/queries/variables";
import { formatUnit } from "../lib/consts";
import { FIBER_OPTICS_COLUMNS } from "../lib/consts.fiber-optics";
import { QueryVariableActual, QueryVariableDefinition } from "../types/queries";

const { t } = useI18n();

const fiberVariableIds = FIBER_OPTICS_COLUMNS.flatMap((column) =>
  column.cards.flatMap((card) => card.variableIds),
);

const { data: definitions } = useQuery<QueryVariableDefinition>({
  query: VARIABLE_DEFINITIONS,
  context: LOADS_CONTEXT,
});

const { data: actuals, executeQuery: refreshActuals } = useQuery<QueryVariableActual>({
  query: VARIABLE_ACTUALS,
  variables: { variables: fiberVariableIds },
  requestPolicy: "network-only",
  context: LOADS_CONTEXT,
});

const { resume: startPolling, pause: stopPolling } = useIntervalFn(refreshActuals, 5000, {
  immediate: false,
});

onMounted(startPolling);
onUnmounted(stopPolling);

const unitById = computed<Record<string, string>>(() =>
  Object.fromEntries(
    (definitions.value?.variables ?? []).map((v) => [v.id, v.variable.unit ?? ""] as const),
  ),
);

const nameById = computed<Record<string, string>>(() =>
  Object.fromEntries(
    (definitions.value?.variables ?? []).map((v) => [v.id, v.variable.name ?? ""] as const),
  ),
);

const valueById = computed<Record<string, number | undefined>>(() =>
  Object.fromEntries(
    (actuals.value?.variables ?? []).map(
      (v) => [v.id, v.actual?.value as number | undefined] as const,
    ),
  ),
);

const formatValue = (value: number | null | undefined): string => {
  if (value == null || Number.isNaN(value)) return "-";
  return Number(value).toFixed(1);
};

const getValue = (variableId: string): string => formatValue(valueById.value[variableId]);

const getUnit = (variableId: string): string => formatUnit(unitById.value[variableId], t);

const getName = (variableId: string): string => nameById.value[variableId] ?? variableId;
</script>

<template>
  <article class="grid grid-cols-1 gap-6 pb-4 lg:grid-cols-2 lg:gap-12">
    <div
      v-for="column in FIBER_OPTICS_COLUMNS"
      :key="column.titleKey"
      class="flex flex-col gap-4"
    >
      <h2 class="text-lg font-semibold">
        {{ t(column.titleKey) }}
      </h2>

      <div class="3xl:grid-cols-3 grid grid-cols-1 gap-3 md:grid-cols-2 md:gap-3">
        <Card
          v-for="card in column.cards"
          :key="card.titleKey"
          class="py-4"
        >
          <CardHeader class="px-4 pb-2">
            <CardTitle class="text-sm">
              {{ t(card.titleKey) }}
            </CardTitle>
          </CardHeader>

          <CardContent class="px-2 pt-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead class="w-24">
                    {{ t("loads.fiberOptics.table.location") }}
                  </TableHead>
                  <TableHead class="text-right">
                    {{ t("loads.fiberOptics.table.value") }}
                  </TableHead>
                  <TableHead class="w-20">
                    {{ t("loads.fiberOptics.table.unit") }}
                  </TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                <TableRow
                  v-for="variableId in card.variableIds"
                  :key="variableId"
                >
                  <TableCell class="font-medium">
                    {{ getName(variableId) }}
                  </TableCell>
                  <TableCell class="text-right font-mono">
                    {{ getValue(variableId) }}
                  </TableCell>
                  <TableCell class="text-muted-foreground">
                    {{ getUnit(variableId) }}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  </article>
</template>
