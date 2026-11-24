import { DEFAULT_SPAN } from "@/modules/thrapp/monitoring/monitoring.consts";
import { createPinia, setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";
import { useMonitoringStore } from "./monitoring";

const HOUR = 3_600_000;
const NOW = Date.parse("2026-11-10T12:00:00Z");

describe("useMonitoringStore", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(NOW);
    setActivePinia(createPinia());
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("starts live on the default span, ending now", () => {
    const store = useMonitoringStore();

    expect(store.live).toBe(true);
    expect(store.resolved).toEqual({ start: NOW - DEFAULT_SPAN, end: NOW });
  });

  it("reloads every chart when the range changes", () => {
    const store = useMonitoringStore();

    store.setRange({ span: HOUR, end: NOW - HOUR });

    expect(store.version).toBe(1);
    expect(store.live).toBe(false);
    expect(store.resolved).toEqual({ start: NOW - 2 * HOUR, end: NOW - HOUR });
  });

  it("steps back and forward by one span, live again once it reaches now", () => {
    const store = useMonitoringStore();

    store.shift(-1);
    expect(store.range).toEqual({ span: DEFAULT_SPAN, end: NOW - DEFAULT_SPAN });

    store.shift(1);
    expect(store.range).toEqual({ span: DEFAULT_SPAN, end: null });
    expect(store.version).toBe(2);
  });

  it("zooms out to twice the span, and reloads in place", () => {
    const store = useMonitoringStore();

    store.zoomOut();
    expect(store.range.span).toBe(2 * DEFAULT_SPAN);

    store.reload();
    expect(store.range.span).toBe(2 * DEFAULT_SPAN);
    expect(store.version).toBe(2);
  });

  it("moves a live range on every refresh, without reloading it", async () => {
    const store = useMonitoringStore();
    await nextTick();

    vi.advanceTimersByTime(store.refreshInterval);

    expect(store.now).toBe(NOW + store.refreshInterval);
    expect(store.version).toBe(0);
  });

  it("stops refreshing a range in the past, or with refresh off", async () => {
    const store = useMonitoringStore();
    store.setRange({ span: HOUR, end: NOW - HOUR });
    await nextTick();
    const now = store.now;

    vi.advanceTimersByTime(5 * store.refreshInterval);
    expect(store.now).toBe(now);

    store.setRange({ span: HOUR, end: null });
    store.refreshInterval = 0;
    await nextTick();
    const live = store.now;

    vi.advanceTimersByTime(5 * 30_000);
    expect(store.now).toBe(live);
  });
});
