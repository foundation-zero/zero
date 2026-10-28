import { createTestingPinia } from "@pinia/testing";
import { createUseQueryFake } from "@tests/lib/urql";
import { useQuery } from "@urql/vue";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ALARMS } from "../graphql/queries/alarms";
import { Alarm } from "../types";
import { QueryAlarms } from "../types/queries";
import { useAlarmsStore } from "./alarms";

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(),
}));

const queries = createUseQueryFake();
const alarmsQuery = () => queries.resultOf<QueryAlarms>(ALARMS);

const alarm = (id: string, variableId: string) =>
  ({ id, actual: { variable: { id: variableId } } }) as Alarm;

describe("loads alarms store", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    queries.reset();
    vi.mocked(useQuery).mockImplementation(queries.useQuery);
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("is ok when there are no active alarms", () => {
    const alarms = useAlarmsStore();

    expect(alarms.status).toBe("ok");
    expect(alarms.activeAlarms).toEqual([]);
  });

  it("is in alarm and lists each alarmed variable once", () => {
    const alarms = useAlarmsStore();

    alarmsQuery().data.value = {
      alarms: [alarm("1", "aws"), alarm("2", "aws"), alarm("3", "main-halyard-load")],
    };

    expect(alarms.status).toBe("alarm");
    expect([...alarms.alarmedVariableIds]).toEqual(["aws", "main-halyard-load"]);
  });

  it("polls for alarms every second only while polling is started", () => {
    const alarms = useAlarmsStore();

    vi.advanceTimersByTime(3000);
    expect(alarmsQuery().executeQuery).not.toHaveBeenCalled();

    alarms.startPolling();
    vi.advanceTimersByTime(3000);
    expect(alarmsQuery().executeQuery).toHaveBeenCalledTimes(3);

    alarms.stopPolling();
    vi.advanceTimersByTime(3000);
    expect(alarmsQuery().executeQuery).toHaveBeenCalledTimes(3);
  });
});
