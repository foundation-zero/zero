import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { EffectScope, effectScope } from "vue";
import client from "../../graphql/client";
import { ACTIVE_ALARMS } from "../../graphql/queries/active-alarms";
import type { AlarmListQueryResponse } from "../../types";
import { useActiveAlarmCount } from "./active-alarms-badge.utils";

vi.mock(import("../../graphql/client"), () => ({
  default: { query: vi.fn() } as never,
}));

const answer = (data: AlarmListQueryResponse | undefined) =>
  vi.mocked(client.query).mockReturnValue({
    toPromise: () => Promise.resolve({ data }),
  } as never);

const list = (...active: (boolean | null)[]): AlarmListQueryResponse => ({
  alerts: {
    alarmList: {
      publishedAt: null,
      recentWindowMinutes: 60,
      alarms: active.map((isActive) => ({ active: isActive }) as never),
    },
  },
});

describe("useActiveAlarmCount", () => {
  let scope: EffectScope;

  beforeEach(() => {
    scope = effectScope();
    vi.useFakeTimers();
  });

  afterEach(() => {
    scope.stop();
    vi.useRealTimers();
  });

  it("counts the active alarms right away", async () => {
    answer(list(true, false, true, null));

    const count = scope.run(() => useActiveAlarmCount(1_000))!;
    await vi.advanceTimersByTimeAsync(0);

    expect(count.value).toBe(2);
    expect(client.query).toHaveBeenCalledWith(ACTIVE_ALARMS, {}, { requestPolicy: "network-only" });
  });

  it("follows changes at the interval", async () => {
    answer(list(true));
    const count = scope.run(() => useActiveAlarmCount(1_000))!;
    await vi.advanceTimersByTimeAsync(0);

    answer(list(true, true, true));
    await vi.advanceTimersByTimeAsync(1_000);

    expect(count.value).toBe(3);
  });

  it("waits for a slow answer instead of asking again", async () => {
    let answerSlowly = (_: { data: AlarmListQueryResponse }) => {};
    vi.mocked(client.query).mockReturnValue({
      toPromise: () => new Promise((resolve) => (answerSlowly = resolve)),
    } as never);
    const count = scope.run(() => useActiveAlarmCount(1_000))!;

    await vi.advanceTimersByTimeAsync(3_000);
    expect(client.query).toHaveBeenCalledTimes(1);

    answerSlowly({ data: list(true) });
    await vi.advanceTimersByTimeAsync(1_000);
    expect(count.value).toBe(1);
    expect(client.query).toHaveBeenCalledTimes(2);
  });

  it("is zero while the list is unavailable", async () => {
    answer({ alerts: { alarmList: null } });
    const offline = scope.run(() => useActiveAlarmCount(1_000))!;
    answer(undefined);
    const failing = scope.run(() => useActiveAlarmCount(1_000))!;
    await vi.advanceTimersByTimeAsync(0);

    expect(offline.value).toBe(0);
    expect(failing.value).toBe(0);
  });
});
