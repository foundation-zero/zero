import { createTestingPinia } from "@pinia/testing";
import { CombinedError } from "@urql/vue";
import { setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import client from "../graphql/client";
import { ALARM_LIST } from "../graphql/queries/alarm-list";
import type { Alarm, AlarmList, AlarmListQueryResponse } from "../types";
import { useAlarmsStore } from "./alarms";

vi.mock(import("../graphql/client"), () => ({
  default: { query: vi.fn() } as never,
}));

type Answer = { data?: AlarmListQueryResponse; error?: CombinedError };

const answer = (result: Answer | Promise<Answer>) =>
  vi.mocked(client.query).mockReturnValue({
    toPromise: () => Promise.resolve(result),
  } as never);

const settle = () => new Promise((resolve) => setTimeout(resolve));

const alarm = (tag: string, fields: Partial<Alarm> = {}): Alarm => ({
  system: "Fresh water",
  tag,
  location: "Engine room",
  description: `${tag} fault`,
  priority: "ALARM",
  active: true,
  acknowledged: false,
  activatedAt: "2026-11-19T10:00:00Z",
  lastChangeAt: "2026-11-19T10:00:00Z",
  lastUpdate: "ACTIVATED",
  ...fields,
});

const list = (alarms: (Alarm | null)[], fields: Partial<AlarmList> = {}) => ({
  alerts: {
    alarmList: {
      publishedAt: "2026-11-19T10:30:00Z",
      recentWindowMinutes: 60,
      alarms,
      ...fields,
    },
  },
});

/** The store, once it received `alarms`. */
const storeWith = async (alarms: (Alarm | null)[], fields: Partial<AlarmList> = {}) => {
  answer({ data: list(alarms, fields) });
  const store = useAlarmsStore();
  await settle();
  return store;
};

const tags = (alarms: Alarm[]) => alarms.map(({ tag }) => tag);

describe("alarms store", () => {
  beforeEach(() => {
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  it("is not loaded before the first answer", () => {
    answer(new Promise(() => {}));
    const store = useAlarmsStore();

    expect(store.loaded).toBe(false);
    expect(store.offline).toBe(false);
    expect(store.activeAlarms).toEqual([]);
  });

  it("splits active alarms from those that ended", async () => {
    const store = await storeWith([alarm("ACTIVE"), alarm("ENDED", { active: false }), null]);

    expect(tags(store.activeAlarms)).toEqual(["ACTIVE"]);
    expect(tags(store.endedAlarms)).toEqual(["ENDED"]);
  });

  it("orders active alarms unacknowledged first, then by priority, then newest", async () => {
    const store = await storeWith([
      alarm("ACKED-GEA", { priority: "GEA", acknowledged: true }),
      alarm("WARNING", { priority: "WARNING" }),
      alarm("OLD-EMERGENCY", { priority: "EMERGENCY", activatedAt: "2026-11-19T09:00:00Z" }),
      alarm("NEW-EMERGENCY", { priority: "EMERGENCY", activatedAt: "2026-11-19T10:10:00Z" }),
      alarm("NO-PRIORITY", { priority: null }),
    ]);

    expect(tags(store.activeAlarms)).toEqual([
      "NEW-EMERGENCY",
      "OLD-EMERGENCY",
      "WARNING",
      "NO-PRIORITY",
      "ACKED-GEA",
    ]);
  });

  it("orders active alarms of unknown activation by their last change", async () => {
    const store = await storeWith([
      alarm("EARLIER", { activatedAt: null, lastChangeAt: "2026-11-19T09:00:00Z" }),
      alarm("LATER", { activatedAt: null, lastChangeAt: "2026-11-19T10:20:00Z" }),
    ]);

    expect(tags(store.activeAlarms)).toEqual(["LATER", "EARLIER"]);
  });

  it("orders ended alarms by their last change, newest first", async () => {
    const store = await storeWith([
      alarm("EARLIER", { active: false, lastChangeAt: "2026-11-19T10:05:00Z" }),
      alarm("LATER", { active: false, lastChangeAt: "2026-11-19T10:25:00Z" }),
      alarm("UNKNOWN", { active: false, lastChangeAt: null }),
    ]);

    expect(tags(store.endedAlarms)).toEqual(["LATER", "EARLIER", "UNKNOWN"]);
  });

  it("takes the window from the list, with a default", async () => {
    const store = await storeWith([], { recentWindowMinutes: 30 });
    expect(store.windowMinutes).toBe(30);

    answer({ data: list([], { recentWindowMinutes: null }) });
    await store.refresh();
    expect(store.windowMinutes).toBe(60);
  });

  it("is offline when the API answers without a list", async () => {
    answer({ data: { alerts: { alarmList: null } } });
    const store = useAlarmsStore();
    await settle();

    expect(store.loaded).toBe(true);
    expect(store.offline).toBe(true);
    expect(store.activeAlarms).toEqual([]);
  });

  it("reports a failed refresh and clears it on the next answer", async () => {
    const store = await storeWith([alarm("A")]);

    answer({ error: new CombinedError({ networkError: new Error("bridge down") }) });
    await store.refresh();
    expect(store.error?.networkError?.message).toBe("bridge down");

    answer({ data: list([alarm("A")]) });
    await store.refresh();
    expect(store.error).toBeUndefined();
  });

  it("asks the alarms client over the network", async () => {
    await storeWith([]);

    expect(client.query).toHaveBeenCalledWith(ALARM_LIST, {}, { requestPolicy: "network-only" });
  });
});
