import {
  ADD_MONITORING_ANNOTATION,
  DELETE_MONITORING_ANNOTATION,
  MONITORING_ANNOTATIONS,
  MONITORING_SERIES,
  MONITORING_STATES,
} from "@/modules/thrapp/graphql/queries/monitoring";
import { type MaybeRefOrGetter, ref, type Ref, shallowRef, toValue, watch } from "vue";
import { client, context } from "./monitoring.client";
import type { MonitoringMetric, MonitoringSignal } from "./monitoring.consts";
import type {
  MetricSeries,
  MonitoringAnnotation,
  ResolvedRange,
  SignalStates,
} from "./monitoring.types";
import { mergeDeviceSeries, mergeSegments } from "./monitoring.utils";

// Kept apart from monitoring.utils so the chart components don't pull in the API client.

export type Timeline = {
  /** The range to show. */
  resolved: Ref<ResolvedRange>;
  /** Changes when the whole range has to load again. */
  version: Ref<number>;
  /** Moves on when an auto-refresh should fetch the newest part. */
  now: Ref<number>;
  /** Whether the range ends at now; only then do refreshes run. */
  live: Ref<boolean>;
};

type Loader<T> = {
  data: Ref<T>;
  loading: Ref<boolean>;
  error: Ref<string | undefined>;
};

const iso = (time: number) => new Date(time).toISOString();

/**
 * Load a query for the range and keep it current: a new range loads in full,
 * a refresh fetches from `overlap(data)` before the last load and merges it in.
 */
function useIncrementalQuery<T, Variables extends object>(
  timeline: Timeline,
  variables: MaybeRefOrGetter<Variables>,
  fetch: (variables: Variables, start: number, end: number, previous: T | undefined) => Promise<T>,
  merge: (previous: T, update: T, windowStart: number) => T,
  overlap: (data: T) => number,
  empty: T,
): Loader<T> {
  const data = shallowRef<T>(empty);
  const loading = ref(false);
  const error = ref<string>();
  let loaded: { until: number; data: T } | undefined;
  let request = 0;

  const load = async (incremental: boolean) => {
    const { start, end } = timeline.resolved.value;
    const previous = incremental ? loaded : undefined;
    const from = previous ? Math.max(start, previous.until - overlap(previous.data)) : start;
    if (from >= end) return;

    const id = ++request;
    loading.value = !previous;
    try {
      const update = await fetch(toValue(variables), from, end, previous?.data);
      if (id !== request) return;
      const next = previous ? merge(previous.data, update, start) : update;
      loaded = { until: end, data: next };
      data.value = next;
      error.value = undefined;
    } catch (failure) {
      if (id !== request) return;
      error.value = failure instanceof Error ? failure.message : String(failure);
    } finally {
      if (id === request) loading.value = false;
    }
  };

  watch(
    () => [timeline.version.value, JSON.stringify(toValue(variables))],
    () => {
      loaded = undefined;
      data.value = empty;
      load(false);
    },
    { immediate: true },
  );
  watch(timeline.now, () => {
    if (timeline.live.value) load(true);
  });

  return { data, loading, error };
}

export type SeriesRequest = {
  module: string;
  metrics: MonitoringMetric[];
  devices?: string[];
};

/** Binned series for one section; refreshes keep the bin size the chart shows. */
export function useMonitoringSeries(
  timeline: Timeline,
  request: MaybeRefOrGetter<SeriesRequest>,
): Loader<MetricSeries[]> {
  const longestBin = (series: MetricSeries[]) =>
    Math.max(0, ...series.map((metric) => metric.binSeconds ?? 0)) * 1000;

  return useIncrementalQuery<MetricSeries[], SeriesRequest>(
    timeline,
    request,
    async ({ module, metrics, devices }, start, end, previous) => {
      const binSeconds = previous ? longestBin(previous) / 1000 || undefined : undefined;
      const result = await client
        .query<{ monitoringSeries: MetricSeries[] }>(
          MONITORING_SERIES,
          { module, metrics, devices, start: iso(start), end: iso(end), binSeconds },
          { ...context, requestPolicy: "network-only" },
        )
        .toPromise();
      if (result.error || !result.data) throw result.error ?? new Error("No data");
      return result.data.monitoringSeries;
    },
    (previous, update, windowStart) =>
      update.map((metric) => ({
        ...metric,
        devices: mergeDeviceSeries(
          previous.find(({ metric: name }) => name === metric.metric)?.devices ?? [],
          metric.devices,
          windowStart,
        ),
      })),
    // Re-fetch the last two bins, as the newest one was still filling up.
    (series) => 2 * longestBin(series),
    [],
  );
}

export type StatesRequest = {
  module: string;
  signals: MonitoringSignal[];
};

/** Mode and state segments for one section. */
export function useMonitoringStates(
  timeline: Timeline,
  request: MaybeRefOrGetter<StatesRequest>,
): Loader<SignalStates[]> {
  return useIncrementalQuery<SignalStates[], StatesRequest>(
    timeline,
    request,
    async ({ module, signals }, start, end) => {
      const result = await client
        .query<{ monitoringStates: SignalStates[] }>(
          MONITORING_STATES,
          { module, signals, start: iso(start), end: iso(end) },
          { ...context, requestPolicy: "network-only" },
        )
        .toPromise();
      if (result.error || !result.data) throw result.error ?? new Error("No data");
      return result.data.monitoringStates;
    },
    (previous, update, windowStart) =>
      update.map((signal) => ({
        ...signal,
        segments: mergeSegments(
          previous.find(({ signal: name }) => name === signal.signal)?.segments ?? [],
          signal.segments,
          windowStart,
        ),
      })),
    // The last segment stays open until the next sample, so fetch the last minute again.
    () => 60_000,
    [],
  );
}

export type AnnotationsRequest = {
  module: string;
  ownerKey: string;
  /** Bump to load again after adding or deleting one. */
  revision: number;
};

/** The annotations in the range; there are few, so every refresh loads them all. */
export function useMonitoringAnnotations(
  timeline: Timeline,
  request: MaybeRefOrGetter<AnnotationsRequest>,
): Loader<MonitoringAnnotation[]> {
  return useIncrementalQuery<MonitoringAnnotation[], AnnotationsRequest>(
    timeline,
    request,
    async ({ module, ownerKey }, start, end) => {
      const result = await client
        .query<{ monitoringAnnotations: MonitoringAnnotation[] }>(
          MONITORING_ANNOTATIONS,
          { module, ownerKey, start: iso(start), end: iso(end) },
          { ...context, requestPolicy: "network-only" },
        )
        .toPromise();
      if (result.error || !result.data) throw result.error ?? new Error("No data");
      return result.data.monitoringAnnotations;
    },
    (_previous, update) => update,
    () => Number.POSITIVE_INFINITY,
    [],
  );
}

export type NewAnnotation = {
  module: string;
  time: number;
  text: string;
  author: string;
  ownerKey: string;
};

export async function addAnnotation({ time, ...annotation }: NewAnnotation) {
  const result = await client
    .mutation(ADD_MONITORING_ANNOTATION, { ...annotation, time: iso(time) }, context)
    .toPromise();
  if (result.error) throw result.error;
}

export async function deleteAnnotation(annotation: MonitoringAnnotation, ownerKey: string) {
  const result = await client
    .mutation(
      DELETE_MONITORING_ANNOTATION,
      { id: annotation.id, time: annotation.time, ownerKey },
      context,
    )
    .toPromise();
  if (result.error) throw result.error;
}
