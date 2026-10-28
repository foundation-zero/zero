import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { computed, type EffectScope, effectScope } from "vue";
import { useBrowserZoomCapture, wheelZoomFactor } from "./browser-zoom";

describe("wheelZoomFactor", () => {
  test("zooms in when scrolling up and out when scrolling down", () => {
    expect(wheelZoomFactor(new WheelEvent("wheel", { deltaY: -10 }))).toBeCloseTo(Math.exp(0.1));
    expect(wheelZoomFactor(new WheelEvent("wheel", { deltaY: 10 }))).toBeCloseTo(Math.exp(-0.1));
  });

  test("caps large deltas and converts lines to pixels", () => {
    const capped = Math.exp(-0.5);

    expect(wheelZoomFactor(new WheelEvent("wheel", { deltaY: 500 }))).toBeCloseTo(capped);
    expect(
      wheelZoomFactor(new WheelEvent("wheel", { deltaY: 1, deltaMode: WheelEvent.DOM_DELTA_LINE })),
    ).toBeCloseTo(Math.exp(-0.16));
  });
});

describe("useBrowserZoomCapture", () => {
  let scope: EffectScope;
  const context = {
    zoom: computed(() => 2),
    zoomTo: vi.fn(),
    zoomIn: vi.fn(),
    zoomOut: vi.fn(),
    fit: vi.fn(),
  };

  const dispatch = <T extends Event>(event: T) => {
    window.dispatchEvent(event);
    return event;
  };

  beforeEach(() => {
    vi.clearAllMocks();
    scope = effectScope();
    scope.run(() => useBrowserZoomCapture(context));
  });

  afterEach(() => {
    scope.stop();
  });

  test("zooms the mimic around the pointer on ctrl + wheel", () => {
    const event = dispatch(
      new WheelEvent("wheel", {
        deltaY: -10,
        ctrlKey: true,
        clientX: 5,
        clientY: 6,
        cancelable: true,
      }),
    );

    expect(event.defaultPrevented).toBe(true);
    expect(context.zoomTo).toHaveBeenCalledWith(2 * Math.exp(0.1), { x: 5, y: 6 });
  });

  test("leaves regular scrolling alone", () => {
    const event = dispatch(new WheelEvent("wheel", { deltaY: -10, cancelable: true }));

    expect(event.defaultPrevented).toBe(false);
    expect(context.zoomTo).not.toHaveBeenCalled();
  });

  test.each([
    ["=", { ctrlKey: true }, "zoomIn"],
    ["+", { metaKey: true }, "zoomIn"],
    ["-", { ctrlKey: true }, "zoomOut"],
    ["0", { metaKey: true }, "fit"],
  ] as const)("handles %s as %s", (key, modifiers, action) => {
    const event = dispatch(new KeyboardEvent("keydown", { key, ...modifiers, cancelable: true }));

    expect(event.defaultPrevented).toBe(true);
    expect(context[action]).toHaveBeenCalledOnce();
  });

  test("ignores other shortcuts and keys without a modifier", () => {
    const events = [
      dispatch(new KeyboardEvent("keydown", { key: "a", ctrlKey: true, cancelable: true })),
      dispatch(new KeyboardEvent("keydown", { key: "=", cancelable: true })),
    ];

    expect(events.some((event) => event.defaultPrevented)).toBe(false);
    expect(context.zoomIn).not.toHaveBeenCalled();
  });

  test("zooms relative to the start of a Safari pinch gesture", () => {
    const gesture = (type: string, scale: number) =>
      Object.assign(new UIEvent(type, { cancelable: true }), { scale, clientX: 5, clientY: 6 });

    expect(dispatch(gesture("gesturestart", 1)).defaultPrevented).toBe(true);
    expect(dispatch(gesture("gesturechange", 1.5)).defaultPrevented).toBe(true);
    expect(context.zoomTo).toHaveBeenCalledWith(3, { x: 5, y: 6 });
  });
});
