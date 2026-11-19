import { beforeEach, describe, expect, it } from "vitest";
import { RIPPLE_DELAY_PER_PIXEL } from "./splash-screen.consts";
import { resetSplashEntry, rippleDelay, takeSplashEntry } from "./splash-screen.utils";

describe("takeSplashEntry", () => {
  beforeEach(resetSplashEntry);

  it("starts cold on the first visit and returns on later visits", () => {
    expect(takeSplashEntry()).toBe("cold");
    expect(takeSplashEntry()).toBe("return");
    expect(takeSplashEntry()).toBe("return");
  });
});

describe("rippleDelay", () => {
  it("grows with the distance from the ripple origin", () => {
    expect(rippleDelay(0, "cold")).toBe(0);
    expect(rippleDelay(500, "cold")).toBe(500 * RIPPLE_DELAY_PER_PIXEL);
  });

  it("is shorter when returning from an app", () => {
    expect(rippleDelay(500, "return")).toBeLessThan(rippleDelay(500, "cold"));
  });
});
