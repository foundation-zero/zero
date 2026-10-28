import { useEventListener } from "@vueuse/core";
import type { MimicZoomContext } from "./context";

/** Zoom factor per pixel of wheel delta; trackpad pinches report small deltas, mouse wheels large. */
const WHEEL_ZOOM_SPEED = 0.01;
/** Caps the wheel delta of a single event, so one mouse wheel notch zooms by about 1.65x at most. */
const MAX_WHEEL_DELTA = 50;
/** Pixels per line for wheel events that report lines, such as Firefox with a mouse wheel. */
const LINE_HEIGHT = 16;

/** Safari's non-standard event for trackpad pinches, which it does not report as wheel events. */
type GestureEvent = UIEvent & { scale: number; clientX: number; clientY: number };

const isZoomShortcut = (event: KeyboardEvent | WheelEvent) =>
  (event.ctrlKey || event.metaKey) && !event.altKey;

export const wheelZoomFactor = ({ deltaY, deltaMode }: WheelEvent) => {
  const pixels = deltaMode === WheelEvent.DOM_DELTA_LINE ? deltaY * LINE_HEIGHT : deltaY;
  const capped = Math.min(MAX_WHEEL_DELTA, Math.max(-MAX_WHEEL_DELTA, pixels));
  return Math.exp(-capped * WHEEL_ZOOM_SPEED);
};

/**
 * Zooms the mimic instead of the page on the browser's zoom gestures and shortcuts: ctrl + wheel
 * and trackpad pinches (which browsers report as ctrl + wheel, or as gesture events in Safari), and
 * ctrl/cmd with +, - or 0. Zooming from the browser's menu or toolbar can't be intercepted.
 */
export const useBrowserZoomCapture = ({
  zoom,
  zoomTo,
  zoomIn,
  zoomOut,
  fit,
}: Pick<MimicZoomContext, "zoom" | "zoomTo" | "zoomIn" | "zoomOut" | "fit">) => {
  useEventListener(
    window,
    "wheel",
    (event: WheelEvent) => {
      if (!event.ctrlKey) return;
      event.preventDefault();
      zoomTo(zoom.value * wheelZoomFactor(event), { x: event.clientX, y: event.clientY });
    },
    { passive: false },
  );

  useEventListener(window, "keydown", (event: KeyboardEvent) => {
    if (!isZoomShortcut(event)) return;

    const action = { "+": zoomIn, "=": zoomIn, "-": zoomOut, _: zoomOut, "0": fit }[event.key];
    if (!action) return;

    event.preventDefault();
    action();
  });

  // Safari reports the scale relative to the start of the pinch.
  let gestureStartZoom = 1;
  useEventListener(window, "gesturestart", (event: Event) => {
    event.preventDefault();
    gestureStartZoom = zoom.value;
  });
  useEventListener(window, "gesturechange", (event: Event) => {
    const { scale, clientX, clientY } = event as GestureEvent;
    event.preventDefault();
    zoomTo(gestureStartZoom * scale, { x: clientX, y: clientY });
  });
};
