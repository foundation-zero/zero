import { useQuery } from "@urql/vue";
import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";
import { POWER_TAGS_CONTEXT } from "../graphql/client";
import { POWER_TAG_PANELS } from "../graphql/queries/power-tag-panels";
import type { PowerTagPanel, PowerTagValues } from "../types";

const ALL_VALUE_COLUMNS = [
  { key: "activePowerTotal", label: "activePowerTotal" },
  { key: "currentA", label: "currentA" },
  { key: "currentB", label: "currentB" },
  { key: "currentC", label: "currentC" },
  { key: "currentN", label: "currentN" },
  { key: "voltageAn", label: "voltageAn" },
  { key: "voltageBn", label: "voltageBn" },
  { key: "voltageCn", label: "voltageCn" },
  { key: "activePowerA", label: "activePowerA" },
  { key: "activePowerB", label: "activePowerB" },
  { key: "activePowerC", label: "activePowerC" },
  { key: "powerFactorA", label: "powerFactorA" },
  { key: "powerFactorB", label: "powerFactorB" },
  { key: "powerFactorC", label: "powerFactorC" },
  { key: "powerFactorTotal", label: "powerFactorTotal" },
] as const satisfies ReadonlyArray<{ key: keyof PowerTagValues; label: string }>;

export const usePowerTagsStore = defineStore("power-tags", () => {
  const { data, fetching, error, executeQuery } = useQuery<{
    powerTagPanels: PowerTagPanel[];
  }>({
    query: POWER_TAG_PANELS,
    requestPolicy: "cache-and-network",
    context: POWER_TAGS_CONTEXT,
  });

  const panels = computed(() => data.value?.powerTagPanels ?? []);

  const sortedPanels = computed(() =>
    panels.value
      .map((panel) => ({
        ...panel,
        powerTags: [...panel.powerTags].toSorted((a, b) => {
          const byComponent = (a.metadata.component ?? "").localeCompare(
            b.metadata.component ?? "",
          );
          if (byComponent !== 0) return byComponent;
          const byConsumer = (a.metadata.consumer ?? "").localeCompare(b.metadata.consumer ?? "");
          if (byConsumer !== 0) return byConsumer;
          return a.topic.localeCompare(b.topic);
        }),
      }))
      .toSorted((a, b) => a.id.localeCompare(b.id)),
  );

  const activePanel = ref("");

  watch(
    () => sortedPanels.value.map((panel) => panel.id),
    (ids) => {
      if (!ids.length) {
        activePanel.value = "";
        return;
      }
      if (!ids.includes(activePanel.value)) {
        activePanel.value = ids[0] ?? "";
      }
    },
    { immediate: true },
  );

  const activePowerTags = computed(
    () => sortedPanels.value.find((panel) => panel.id === activePanel.value)?.powerTags ?? [],
  );

  const unitByName = computed<Record<string, string | null>>(() =>
    Object.fromEntries(
      (activePowerTags.value[0]?.metadata.values ?? []).map(
        (meta) => [meta.name, meta.unit] as const,
      ),
    ),
  );

  const allReadingsNull = computed(
    () =>
      activePowerTags.value.length > 0 &&
      activePowerTags.value.every((tag) =>
        Object.values(tag.values).every((reading) => reading === null),
      ),
  );

  const showAll = ref(false);

  const visibleColumns = computed(() =>
    showAll.value ? ALL_VALUE_COLUMNS : ALL_VALUE_COLUMNS.slice(0, 1),
  );

  const refresh = () => executeQuery({ requestPolicy: "network-only" });

  return {
    sortedPanels,
    activePanel,
    activePowerTags,
    unitByName,
    allReadingsNull,
    showAll,
    visibleColumns,
    fetching,
    error,
    refresh,
  };
});
