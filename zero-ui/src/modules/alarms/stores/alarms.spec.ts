import { createTestingPinia } from "@pinia/testing";
import { createUseQueryFake } from "@tests/lib/urql";
import { useQuery } from "@urql/vue";
import { setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ALARM_LIST } from "../graphql/queries/alarm-list";
import type { Alarm, AlarmList, AlarmListQueryResponse } from "../types";
import { useAlarmsStore } from "./alarms";

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(),
}));

const queries = createUseQueryFake();
const alarmListQuery = () => queries.resultOf<AlarmListQueryResponse>(ALARM_LIST);

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

const receive = (alarms: (Alarm | null)[], fields: Partial<AlarmList> = {}) => {
  alarmListQuery().data.value = {
    alerts: {
      alarmList: {
        publishedAt: "2026-11-19T10:30:00Z",
        recentWindowMinutes: 60,
        alarms,
        ...fields,
      },
    },
  };
};

const tags = (alarms: Alarm[]) => alarms.map(({ tag }) => tag);

describe("alarms store", () => {
  beforeEach(() => {
    queries.reset();
    vi.mocked(useQuery).mockImplementation(queries.useQuery);
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  it("is not loaded before the first answer", () => {
    const store = useAlarmsStore();

    expect(store.loaded).toBe(false);
    expect(store.offline).toBe(false);
    expect(store.activeAlarms).toEqual([]);
  });

  it("splits active alarms from those that ended", () => {
    const store = useAlarmsStore();

    receive([alarm("ACTIVE"), alarm("ENDED", { active: false }), null]);

    expect(tags(store.activeAlarms)).toEqual(["ACTIVE"]);
    expect(tags(store.endedAlarms)).toEqual(["ENDED"]);
  });

  it("orders active alarms unacknowledged first, then by priority, then newest", () => {
    const store = useAlarmsStore();

    receive([
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

  it("orders active alarms of unknown activation by their last change", () => {
    const store = useAlarmsStore();

    receive([
      alarm("EARLIER", { activatedAt: null, lastChangeAt: "2026-11-19T09:00:00Z" }),
      alarm("LATER", { activatedAt: null, lastChangeAt: "2026-11-19T10:20:00Z" }),
    ]);

    expect(tags(store.activeAlarms)).toEqual(["LATER", "EARLIER"]);
  });

  it("orders ended alarms by their last change, newest first", () => {
    const store = useAlarmsStore();

    receive([
      alarm("EARLIER", { active: false, lastChangeAt: "2026-11-19T10:05:00Z" }),
      alarm("LATER", { active: false, lastChangeAt: "2026-11-19T10:25:00Z" }),
      alarm("UNKNOWN", { active: false, lastChangeAt: null }),
    ]);

    expect(tags(store.endedAlarms)).toEqual(["LATER", "EARLIER", "UNKNOWN"]);
  });

  it("takes the window from the list, with a default", () => {
    const store = useAlarmsStore();

    receive([], { recentWindowMinutes: 30 });
    expect(store.windowMinutes).toBe(30);

    receive([], { recentWindowMinutes: null });
    expect(store.windowMinutes).toBe(60);
  });

  it("is offline when the API answers without a list", () => {
    const store = useAlarmsStore();

    alarmListQuery().data.value = { alerts: { alarmList: null } };

    expect(store.loaded).toBe(true);
    expect(store.offline).toBe(true);
    expect(store.activeAlarms).toEqual([]);
  });

  it("refreshes from the network", async () => {
    const store = useAlarmsStore();

    await store.refresh();

    expect(alarmListQuery().executeQuery).toHaveBeenCalledWith({ requestPolicy: "network-only" });
  });
});
