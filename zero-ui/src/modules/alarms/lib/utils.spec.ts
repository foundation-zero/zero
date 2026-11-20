import { describe, expect, it, vi } from "vitest";
import { isActive, skipWhilePending } from "./utils";

describe("isActive", () => {
  it.each([
    [{ active: true }, true],
    [{ active: false }, false],
    [{ active: null }, false],
    [null, false],
  ])("%o is active: %s", (alarm, expected) => {
    expect(isActive(alarm)).toBe(expected);
  });
});

describe("skipWhilePending", () => {
  it("skips calls while the request runs, and runs again after", async () => {
    let finish = () => {};
    const request = vi.fn(() => new Promise<void>((resolve) => (finish = resolve)));
    const refresh = skipWhilePending(request);

    const first = refresh();
    await refresh();
    expect(request).toHaveBeenCalledTimes(1);

    finish();
    await first;
    void refresh();
    expect(request).toHaveBeenCalledTimes(2);
  });

  it("runs again after a failed request", async () => {
    const request = vi.fn().mockRejectedValueOnce(new Error("down")).mockResolvedValue(undefined);
    const refresh = skipWhilePending(request);

    await expect(refresh()).rejects.toThrow("down");
    await refresh();

    expect(request).toHaveBeenCalledTimes(2);
  });
});
