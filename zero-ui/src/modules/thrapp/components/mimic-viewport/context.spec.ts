import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { type EffectScope, effectScope, nextTick, reactive, toRefs } from "vue";
import { createMimicZoomContext, type MimicZoomContext } from "./context";
import { MAX_ZOOM, MIN_ZOOM, ZOOM_STEP } from "./zoom";

// jsdom has no ResizeObserver, so the viewport size is set by the tests.
const viewportSize = vi.hoisted(() => ({ width: 0, height: 0 }));

vi.mock("@vueuse/core", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@vueuse/core")>()),
  useElementSize: () => toRefs(reactive(viewportSize)),
}));

const createSvg = (width: number, height: number) => {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  Object.defineProperty(svg, "viewBox", { value: { baseVal: { width, height } } });
  return svg;
};

const createScroller = (width: number, height: number) => {
  const scroller = document.createElement("div");
  Object.defineProperties(scroller, {
    clientWidth: { value: width },
    clientHeight: { value: height },
    scrollLeft: { value: 0, writable: true },
    scrollTop: { value: 0, writable: true },
  });
  return scroller;
};

describe("createMimicZoomContext", () => {
  let scope: EffectScope;
  let context: MimicZoomContext;
  let content: HTMLElement;

  /** Hands a viewport of the given size and a mimic with the given viewBox to the context. */
  const mount = async (
    viewport = { width: 800, height: 400 },
    mimic = { width: 1000, height: 400 },
  ) => {
    Object.assign(viewportSize, viewport);
    context.scroller.value = createScroller(viewport.width, viewport.height);
    content.append(createSvg(mimic.width, mimic.height));
    context.content.value = content;
    await nextTick();
  };

  beforeEach(() => {
    Object.assign(viewportSize, { width: 0, height: 0 });
    content = document.createElement("div");
    scope = effectScope();
    context = scope.run(() => createMimicZoomContext())!;
  });

  afterEach(() => {
    scope.stop();
  });

  test("has no content size until the mimic's SVG is known", () => {
    expect(context.zoom.value).toBe(1);
    expect(context.contentStyle.value).toBeUndefined();
  });

  test("fits the mimic in the viewport", async () => {
    await mount({ width: 800, height: 400 }, { width: 1000, height: 400 });

    expect(context.fitting.value).toBe(true);
    expect(context.zoom.value).toBe(0.8);
    expect(context.contentStyle.value).toEqual({ width: "800px", height: "320px" });
  });

  test("follows the viewport size while fitting", async () => {
    await mount({ width: 800, height: 400 }, { width: 1000, height: 400 });

    viewportSize.height = 200;

    expect(context.zoom.value).toBe(0.5);
  });

  test("reads the SVG when it is rendered after the content element", async () => {
    context.scroller.value = createScroller(500, 500);
    Object.assign(viewportSize, { width: 500, height: 500 });
    context.content.value = content;
    await nextTick();

    expect(context.contentStyle.value).toBeUndefined();

    content.append(createSvg(250, 100));
    await vi.waitFor(() => expect(context.zoom.value).toBe(2));
  });

  test("zooms in and out by a step and stops fitting", async () => {
    await mount();

    await context.zoomIn();
    expect(context.fitting.value).toBe(false);
    expect(context.zoom.value).toBeCloseTo(0.8 * ZOOM_STEP);

    await context.zoomOut();
    expect(context.zoom.value).toBeCloseTo(0.8);
  });

  test("clamps the zoom to the limits", async () => {
    await mount();

    for (let i = 0; i < 20; i++) await context.zoomIn();
    expect(context.zoom.value).toBe(MAX_ZOOM);
    expect(context.canZoomIn.value).toBe(false);

    for (let i = 0; i < 20; i++) await context.zoomOut();
    expect(context.zoom.value).toBe(MIN_ZOOM);
    expect(context.canZoomOut.value).toBe(false);
  });

  test("switches between the actual size and fitting", async () => {
    await mount();

    await context.actualSize();
    expect(context.zoom.value).toBe(1);
    expect(context.contentStyle.value).toEqual({ width: "1000px", height: "400px" });

    context.fit();
    expect(context.fitting.value).toBe(true);
    expect(context.zoom.value).toBe(0.8);
  });

  test("keeps the centre of the viewport in place when zooming", async () => {
    await mount({ width: 800, height: 400 }, { width: 800, height: 400 });
    // The mimic starts at the top left of the viewport, at a zoom of 1.
    vi.spyOn(context.scroller.value!, "getBoundingClientRect").mockReturnValue(new DOMRect());
    vi.spyOn(content, "getBoundingClientRect").mockReturnValue(new DOMRect());

    await context.zoomIn();

    // The centre (400, 200) moves to (500, 250) at a zoom of 1.25, so the viewport scrolls along.
    expect(context.scroller.value!.scrollLeft).toBe(100);
    expect(context.scroller.value!.scrollTop).toBe(50);
  });

  test("does nothing without a viewport", async () => {
    await context.zoomIn();

    expect(context.fitting.value).toBe(true);
    expect(context.zoom.value).toBe(1);
  });
});
