import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { effectScope } from "vue";
import { UNLOCK_COUNTDOWN_SECONDS } from "./manual-mode-toggle.consts";
import { useManualModeUnlock } from "./manual-mode-toggle.utils";

const setup = (matchPassword: string | undefined = "secret") => {
  const unlock = vi.fn();
  const scope = effectScope();
  const state = scope.run(() => useManualModeUnlock(matchPassword, unlock))!;
  return { unlock, state, scope };
};

describe("useManualModeUnlock", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it("counts down from ten seconds before unlocking", () => {
    const { unlock, state } = setup();
    state.password.value = "secret";

    state.confirm();
    expect(state.isActive.value).toBe(true);
    expect(state.remaining.value).toBe(UNLOCK_COUNTDOWN_SECONDS);

    vi.advanceTimersByTime(3000);
    expect(state.remaining.value).toBe(7);
    expect(unlock).not.toHaveBeenCalled();

    vi.advanceTimersByTime(7000);
    expect(unlock).toHaveBeenCalledOnce();
    expect(state.isActive.value).toBe(false);
  });

  it("does not start with a wrong password", () => {
    const { unlock, state } = setup();
    state.password.value = "guess";

    state.confirm();
    vi.advanceTimersByTime(UNLOCK_COUNTDOWN_SECONDS * 1000);

    expect(state.isValid.value).toBe(false);
    expect(unlock).not.toHaveBeenCalled();
  });

  it("never accepts a password when none is configured", () => {
    const { state } = setup(undefined);
    state.password.value = "";

    expect(state.isValid.value).toBe(false);
  });

  it("stops and resets the countdown on cancel", () => {
    const { unlock, state } = setup();
    state.password.value = "secret";

    state.confirm();
    vi.advanceTimersByTime(4000);
    state.cancel();
    vi.advanceTimersByTime(UNLOCK_COUNTDOWN_SECONDS * 1000);

    expect(unlock).not.toHaveBeenCalled();
    expect(state.isActive.value).toBe(false);
    expect(state.remaining.value).toBe(UNLOCK_COUNTDOWN_SECONDS);
  });
});
