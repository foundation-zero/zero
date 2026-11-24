<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { MonitoringSection } from "@/modules/thrapp/monitoring/components/monitoring-section";
import { StatePanel } from "@/modules/thrapp/monitoring/components/state-panel";
import { TimeRangePicker } from "@/modules/thrapp/monitoring/components/time-range-picker";
import { TrendPanel } from "@/modules/thrapp/monitoring/components/trend-panel";
import { AnnotationLayer } from "@/modules/thrapp/monitoring/components/annotation-layer";
import { AnnotationToolbar } from "@/modules/thrapp/monitoring/components/annotation-toolbar";
import {
  addAnnotation,
  deleteAnnotation,
  useMonitoringAnnotations,
  useMonitoringStates,
} from "@/modules/thrapp/monitoring/monitoring-data.utils";
import { ANNOTATION_KINDS, MODULE_MONITORING } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  AnnotationKind,
  MonitoringAnnotation,
  ResolvedRange,
} from "@/modules/thrapp/monitoring/monitoring.types";
import {
  rangeFromQuery,
  rangeToQuery,
  useAnnotationIdentity,
  zoomedRange,
} from "@/modules/thrapp/monitoring/monitoring.utils";
import { useLocalStorage } from "@vueuse/core";
import { useMonitoringStore } from "@/modules/thrapp/stores/monitoring";
import { storeToRefs } from "pinia";
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const GROUP = "thrs-monitoring";

const t = tScoped("thrapp.monitoring");
const route = useRoute();
const router = useRouter();

const store = useMonitoringStore();
const { range, refreshInterval, resolved, version, now, live } = storeToRefs(store);
const timeline = { resolved, version, now, live };

const moduleKey = computed(() => String(route.params.module));
const config = computed(() => MODULE_MONITORING[moduleKey.value]);

// The URL holds the range, so a view can be shared and survives a reload.
store.setRange(rangeFromQuery(route.query));
watch(range, (next) => {
  const query = rangeToQuery(next);
  if (query.range !== route.query.range || query.end !== route.query.end) {
    router.replace({ query: { ...route.query, ...query } });
  }
});
watch(
  () => [route.query.range, route.query.end],
  () => {
    const next = rangeFromQuery(route.query);
    if (next.span !== range.value.span || next.end !== range.value.end) store.setRange(next);
  },
);

// All mode and state signals in one request: the state cards and the bands behind
// the trends share them.
const signals = computed(() => [
  ...new Set([
    ...(config.value?.states ?? []).flatMap(({ panels }) =>
      panels.flatMap(({ rows }) => rows.map(({ signal }) => signal)),
    ),
    ...(config.value?.trends ?? []).flatMap(({ panels }) =>
      panels.flatMap(({ overlays }) => (overlays ?? []).map(({ signal }) => signal)),
    ),
  ]),
]);
const states = useMonitoringStates(timeline, () => ({
  module: config.value?.module ?? "",
  signals: signals.value,
}));

const setRange = (next: typeof range.value) => store.setRange(next);

// Annotations: the crew's notes, parameter changes and alarms on every timeline.
const { ownerKey, author } = useAnnotationIdentity();
const revision = ref(0);
const annotations = useMonitoringAnnotations(timeline, () => ({
  module: config.value?.module ?? "",
  ownerKey: ownerKey.value,
  revision: revision.value,
}));
const shownKinds = useLocalStorage<AnnotationKind[]>("thrs-monitoring-annotation-kinds", [
  ...ANNOTATION_KINDS,
]);
const shownSet = computed(() => new Set<string>(shownKinds.value));
const saving = ref(false);
const annotationError = ref<string>();

const addNote = async ({ time, text }: { time: number; text: string }) => {
  if (!config.value) return;
  saving.value = true;
  annotationError.value = undefined;
  try {
    await addAnnotation({
      module: config.value.module,
      time,
      text,
      author: author.value,
      ownerKey: ownerKey.value,
    });
    revision.value++;
  } catch (failure) {
    annotationError.value = failure instanceof Error ? failure.message : String(failure);
  } finally {
    saving.value = false;
  }
};
const removeNote = async (annotation: MonitoringAnnotation) => {
  await deleteAnnotation(annotation, ownerKey.value);
  revision.value++;
};
const zoomTo = (next: ResolvedRange) => store.setRange(zoomedRange(next, Date.now()));
</script>

<template>
  <p
    v-if="!config"
    class="text-muted-foreground p-6"
  >
    {{ t("notAvailable") }}
  </p>
  <div
    v-else
    class="-mx-4 h-full overflow-y-auto px-4 md:-mx-6 md:px-6"
  >
    <header
      class="bg-muted/95 z-20 flex flex-wrap items-center justify-between gap-4 pt-4 pb-4 backdrop-blur-sm md:sticky md:top-0"
    >
      <h1
        class="font-headers text-foreground text-xl leading-7 font-semibold sm:text-2xl sm:leading-8"
      >
        {{ t("title", { module: t(`modules.${moduleKey}`) }) }}
      </h1>
      <TimeRangePicker
        :model-value="range"
        :interval="refreshInterval"
        @update:model-value="setRange"
        @update:interval="refreshInterval = $event"
        @refresh="store.reload()"
      />
      <AnnotationToolbar
        v-model:shown="shownKinds"
        v-model:author="author"
        class="w-full justify-end"
        :annotations="annotations.data.value"
        :default-time="resolved.end"
        :saving="saving"
        :error="annotationError"
        @add="addNote"
      />
    </header>

    <div class="flex flex-col gap-10 pt-2 pb-8">
      <MonitoringSection
        v-for="group in config.states"
        :key="group.section"
        :title="t(`sections.${group.section}`)"
        :storage-key="`${moduleKey}:${group.section}`"
      >
        <MonitoringSection
          v-for="panel in group.panels"
          :key="panel.key"
          :title="t(`sections.${panel.key}`)"
          :storage-key="`${moduleKey}:${panel.key}`"
          level="group"
        >
          <StatePanel
            :config="panel"
            :states="states.data.value"
            :range="resolved"
            :loading="states.loading.value"
            :error="states.error.value"
            @zoom="zoomTo"
          >
            <template #overlay>
              <AnnotationLayer
                :annotations="annotations.data.value"
                :shown="shownSet"
                :range="resolved"
                :bottom="24"
                @delete="removeNote"
              />
            </template>
          </StatePanel>
        </MonitoringSection>
      </MonitoringSection>

      <MonitoringSection
        v-for="group in config.trends"
        :key="group.section"
        :title="t(`sections.${group.section}`)"
        :storage-key="`${moduleKey}:${group.section}`"
      >
        <MonitoringSection
          v-for="panel in group.panels"
          :key="panel.key"
          :title="t(`sections.${panel.key}`)"
          :storage-key="`${moduleKey}:${panel.key}`"
          level="group"
        >
          <TrendPanel
            :config="panel"
            :module="config.module"
            :timeline="timeline"
            :states="states.data.value"
            :group="GROUP"
            @zoom="zoomTo"
          >
            <template #overlay="{ top, bottom }">
              <AnnotationLayer
                :annotations="annotations.data.value"
                :shown="shownSet"
                :range="resolved"
                :top="top"
                :bottom="bottom"
                @delete="removeNote"
              />
            </template>
          </TrendPanel>
        </MonitoringSection>
      </MonitoringSection>
    </div>
  </div>
</template>
