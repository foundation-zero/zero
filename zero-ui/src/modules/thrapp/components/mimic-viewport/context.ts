import { useElementSize, useMutationObserver } from "@vueuse/core";
import { createContext } from "reka-ui";
import { computed, type ComputedRef, nextTick, type Ref, ref, shallowRef, watch } from "vue";
import { MAX_ZOOM, MIN_ZOOM, ZOOM_STEP } from "./zoom";

export type ZoomPoint = { x: number; y: number };

export type MimicZoomContext = {
  /** The scroll container of the viewport, set by `MimicViewport`. */
  scroller: Ref<HTMLElement | undefined>;
  /** The element that holds the mimic's root SVG, set by `MimicViewport`. */
  content: Ref<HTMLElement | undefined>;
  /** Size of the content element for the current zoom. */
  contentStyle: ComputedRef<{ width: string; height: string } | undefined>;
  /** Whether the zoom follows the viewport size. */
  fitting: Ref<boolean>;
  zoom: ComputedRef<number>;
  canZoomIn: ComputedRef<boolean>;
  canZoomOut: ComputedRef<boolean>;
  zoomTo: (zoom: number, point?: ZoomPoint) => Promise<void>;
  zoomIn: () => Promise<void>;
  zoomOut: () => Promise<void>;
  actualSize: () => Promise<void>;
  fit: () => void;
};

export const [injectMimicZoomContext, provideMimicZoomContext] =
  createContext<MimicZoomContext>("MimicZoomContext");

const clamp = (value: number) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, value));

export const createMimicZoomContext = (): MimicZoomContext => {
  const scroller = shallowRef<HTMLElement>();
  const content = shallowRef<HTMLElement>();

  // Intrinsic size of the mimic, taken from the viewBox of its root SVG. At a zoom of 1, one SVG
  // unit is one CSS pixel.
  const intrinsic = ref<{ width: number; height: number }>();
  const readIntrinsicSize = () => {
    const viewBox = content.value?.querySelector("svg")?.viewBox.baseVal;
    if (viewBox?.width && viewBox.height) {
      intrinsic.value = { width: viewBox.width, height: viewBox.height };
    }
  };
  // Read once the viewport hands over its content element, and again when the SVG changes: mimics
  // are async components, so their SVG may only appear after the content is mounted.
  watch(content, readIntrinsicSize, { flush: "post" });
  useMutationObserver(content, readIntrinsicSize, { childList: true, subtree: true });

  const { width: viewportWidth, height: viewportHeight } = useElementSize(scroller);

  // In fit mode the zoom follows the viewport size; any other zoom action switches to a fixed zoom.
  const fitting = ref(true);
  const fixedZoom = ref(1);

  const fitZoom = computed(() => {
    if (!intrinsic.value || !viewportWidth.value || !viewportHeight.value) return 1;
    return Math.min(
      viewportWidth.value / intrinsic.value.width,
      viewportHeight.value / intrinsic.value.height,
    );
  });
  const zoom = computed(() => (fitting.value ? fitZoom.value : fixedZoom.value));

  const contentStyle = computed(() =>
    intrinsic.value
      ? {
          width: `${Math.floor(intrinsic.value.width * zoom.value)}px`,
          height: `${Math.floor(intrinsic.value.height * zoom.value)}px`,
        }
      : undefined,
  );

  /**
   * Zooms to a fixed level while keeping the given point (in client coordinates) in place. Without
   * a point, or with one outside the viewport, the centre of the viewport stays in place.
   */
  const zoomTo = async (next: number, point?: ZoomPoint) => {
    const viewport = scroller.value;
    const mimic = content.value;
    if (!viewport || !mimic) return;

    const previous = zoom.value;
    // Fitting can go beyond the limits (e.g. a wide mimic on a phone). Clamping a request to zoom
    // further out (or in) would then do the opposite, so it is ignored instead.
    if ((next < previous && previous <= MIN_ZOOM) || (next > previous && previous >= MAX_ZOOM)) {
      return;
    }

    const viewportBox = viewport.getBoundingClientRect();
    const inViewport =
      point &&
      point.x >= viewportBox.left &&
      point.x <= viewportBox.left + viewport.clientWidth &&
      point.y >= viewportBox.top &&
      point.y <= viewportBox.top + viewport.clientHeight;
    const centerX = inViewport ? point.x : viewportBox.left + viewport.clientWidth / 2;
    const centerY = inViewport ? point.y : viewportBox.top + viewport.clientHeight / 2;
    const before = mimic.getBoundingClientRect();
    const focusX = (centerX - before.left) / previous;
    const focusY = (centerY - before.top) / previous;

    fixedZoom.value = clamp(next);
    fitting.value = false;
    await nextTick();

    const after = mimic.getBoundingClientRect();
    viewport.scrollLeft += after.left + focusX * fixedZoom.value - centerX;
    viewport.scrollTop += after.top + focusY * fixedZoom.value - centerY;
  };

  return {
    scroller,
    content,
    contentStyle,
    fitting,
    zoom,
    canZoomIn: computed(() => zoom.value < MAX_ZOOM),
    canZoomOut: computed(() => zoom.value > MIN_ZOOM),
    zoomTo,
    zoomIn: () => zoomTo(zoom.value * ZOOM_STEP),
    zoomOut: () => zoomTo(zoom.value / ZOOM_STEP),
    actualSize: () => zoomTo(1),
    fit: () => (fitting.value = true),
  };
};
