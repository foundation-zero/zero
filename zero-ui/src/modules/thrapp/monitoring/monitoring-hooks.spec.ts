import { ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import { afterEach, describe, expect, it, vi } from "vitest";
import { effectScope, nextTick, ref } from "vue";
import { MonitoringSignal } from "./monitoring.consts";
import type { ResolvedRange } from "./monitoring.types";
import {
  tickLabel,
  useAnnotationIdentity,
  useDurationFormat,
  usePlotDrag,
  useStateStyles,
  useThemeMode,
} from "./monitoring.utils";

// The composables translate through useI18n; give them the app's messages.
vi.mock(import("vue-i18n"), async (importOriginal) => {
  const original = await importOriginal();
  const { default: en } = await import("@/modules/thrapp/i18n/en.json");
  const i18n = original.createI18n({ legacy: false, locale: "en", messages: { en } });
  return { ...original, useI18n: (() => i18n.global) as unknown as typeof original.useI18n };
});

const HOUR = 3_600_000;
const NOW = Date.parse("2026-11-10T12:00:00Z");

const inScope = <T>(run: () => T) => {
  const scope = effectScope();
  const result = scope.run(run)!;
  return { result, stop: () => scope.stop() };
};

describe("tickLabel", () => {
  it("shows the time of day up to two days, and the date beyond", () => {
    const tick = Date.parse("2026-11-10T09:30:00");

    expect(tickLabel(tick, { start: NOW - 6 * HOUR, end: NOW })).toBe("09:30");
    expect(tickLabel(tick, { start: NOW - 7 * 24 * HOUR, end: NOW })).toBe("10 Nov");
  });
});

describe("useDurationFormat", () => {
  const format = inScope(() => useDurationFormat()).result;

  it("names each part from the largest unit down, leaving out leading zeros", () => {
    expect(format(2 * 3600 + 30 * 60 + 10)).toBe("2hr 30 min 10 sec");
    expect(format(45)).toBe("45 sec");
  });

  it("keeps only as many units as asked for", () => {
    expect(format(6 * 86_400 + 12 * 3600 + 5 * 60, 2)).toBe("6d 12hr");
  });

  it("shows zero seconds for no time at all", () => {
    expect(format(0)).toBe("0 sec");
  });
});

describe("useStateStyles", () => {
  const styleOf = inScope(() => useStateStyles()).result;

  it("gives a state its mimic colour and label", () => {
    expect(styleOf(MonitoringSignal.BoostingMode, "boosting_high_temperature")).toEqual({
      mode: ModeBadgeMode.Boosting,
      label: "Boosting HT",
    });
  });

  it("labels the three tanks from one list", () => {
    expect(styleOf(MonitoringSignal.Tank2State, "needs boost").label).toBe("Needs boost");
  });

  it("falls back to the raw state and an idle colour for a state it doesn't know", () => {
    expect(styleOf(MonitoringSignal.FillingMode, "draining")).toEqual({
      mode: ModeBadgeMode.Idle,
      label: "draining",
    });
  });
});

describe("useThemeMode", () => {
  afterEach(() => {
    document.documentElement.classList.remove("dark");
    document.body.innerHTML = "";
  });

  it("follows the dark class on the page", async () => {
    const element = document.createElement("div");
    document.body.append(element);
    const { result, stop } = inScope(() => useThemeMode(ref(element)));

    expect(result.mode.value).toBe("light");

    document.documentElement.classList.add("dark");
    await nextTick();
    await new Promise((resolve) => setTimeout(resolve));
    expect(result.mode.value).toBe("dark");
    stop();
  });
});

describe("usePlotDrag", () => {
  const RANGE: ResolvedRange = { start: NOW - 10 * HOUR, end: NOW };
  // A 1100 px wide container with a 50 px label column on the left: a 1000 px plot.
  const INSET = { left: 50, right: 50 };

  const setup = () => {
    const element = document.createElement("div");
    element.getBoundingClientRect = () => ({ left: 0, width: 1100 }) as DOMRect;
    document.body.append(element);
    const onZoom = vi.fn();
    const { result, stop } = inScope(() => usePlotDrag(ref(element), RANGE, INSET, onZoom));
    const pointer = (type: string, clientX: number, target: EventTarget = window) =>
      target.dispatchEvent(new MouseEvent(type, { clientX, button: 0, bubbles: true }));
    return { element, onZoom, pointer, stop, ...result };
  };

  it("zooms to the stretch of time dragged across, in either direction", () => {
    const { element, onZoom, pointer, selection, stop } = setup();

    pointer("pointerdown", 850, element);
    pointer("pointermove", 250);
    expect(selection.value).toEqual({ left: 250, width: 600 });

    pointer("pointerup", 250);
    expect(onZoom).toHaveBeenCalledWith({ start: NOW - 8 * HOUR, end: NOW - 2 * HOUR });
    expect(selection.value).toBeNull();
    stop();
  });

  it("treats a short drag as a click", () => {
    const { element, onZoom, pointer, dragging, stop } = setup();

    pointer("pointerdown", 300, element);
    expect(dragging.value).toBe(true);
    pointer("pointermove", 303);
    pointer("pointerup", 303);

    expect(onZoom).not.toHaveBeenCalled();
    expect(dragging.value).toBe(false);
    stop();
  });

  it("ignores a press on the labels, and clamps a drag to the plot", () => {
    const { element, onZoom, pointer, stop } = setup();

    pointer("pointerdown", 20, element);
    pointer("pointerup", 600);
    expect(onZoom).not.toHaveBeenCalled();

    pointer("pointerdown", 550, element);
    pointer("pointermove", 2000);
    pointer("pointerup", 2000);
    expect(onZoom).toHaveBeenCalledWith({ start: NOW - 5 * HOUR, end: NOW });
    stop();
  });
});

describe("useAnnotationIdentity", () => {
  afterEach(() => localStorage.clear());

  it("keeps one owner key per browser, and the name typed last", async () => {
    const first = inScope(() => useAnnotationIdentity());
    first.result.author.value = "Bosun";
    await nextTick();
    const key = first.result.ownerKey.value;
    first.stop();

    const second = inScope(() => useAnnotationIdentity());
    expect(second.result.ownerKey.value).toBe(key);
    expect(second.result.author.value).toBe("Bosun");
    second.stop();
  });
});
