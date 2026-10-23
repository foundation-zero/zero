<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { useElementSize, useMutationObserver } from "@vueuse/core";
import { computed, type HTMLAttributes, nextTick, onMounted, ref, useTemplateRef } from "vue";
import { MAX_ZOOM, MIN_ZOOM, ZOOM_STEP } from "./zoom";
import ZoomControls from "./ZoomControls.vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();

const scroller = useTemplateRef<HTMLElement>("scroller");
const content = useTemplateRef<HTMLElement>("content");

// Intrinsic size of the mimic, taken from the viewBox of its root SVG. At a zoom of 1, one SVG unit
// is one CSS pixel.
const intrinsic = ref<{ width: number; height: number }>();
const readIntrinsicSize = () => {
  const viewBox = content.value?.querySelector("svg")?.viewBox.baseVal;
  if (viewBox?.width && viewBox.height) {
    intrinsic.value = { width: viewBox.width, height: viewBox.height };
  }
};
// Mimics are async components, so their SVG may only appear after mounting.
useMutationObserver(content, readIntrinsicSize, { childList: true, subtree: true });
onMounted(readIntrinsicSize);

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

const clamp = (value: number) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, value));

/** Zooms to a fixed level while keeping the point in the centre of the viewport in place. */
const zoomTo = async (next: number) => {
  const viewport = scroller.value;
  const mimic = content.value;
  if (!viewport || !mimic) return;

  const previous = zoom.value;
  const viewportBox = viewport.getBoundingClientRect();
  const centerX = viewportBox.left + viewport.clientWidth / 2;
  const centerY = viewportBox.top + viewport.clientHeight / 2;
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

const zoomIn = () => zoomTo(zoom.value * ZOOM_STEP);
const zoomOut = () => zoomTo(zoom.value / ZOOM_STEP);
const actualSize = () => zoomTo(1);
const fit = () => (fitting.value = true);
</script>

<template>
  <div :class="cn('relative', props.class)">
    <!-- Auto margins centre the mimic while it fits and still allow scrolling to every edge. -->
    <div
      ref="scroller"
      class="flex size-full"
      :class="fitting ? 'overflow-hidden' : 'overflow-auto'"
    >
      <div
        ref="content"
        class="m-auto shrink-0 [&>svg]:block [&>svg]:size-full"
        :style="contentStyle"
      >
        <slot />
      </div>
    </div>

    <ZoomControls
      class="absolute right-3 bottom-3"
      :can-zoom-in="zoom < MAX_ZOOM"
      :can-zoom-out="zoom > MIN_ZOOM"
      @zoom-in="zoomIn"
      @zoom-out="zoomOut"
      @actual-size="actualSize"
      @fit="fit"
    />
  </div>
</template>
