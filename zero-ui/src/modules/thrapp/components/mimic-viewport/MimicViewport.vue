<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import type { HTMLAttributes } from "vue";
import { useBrowserZoomCapture } from "./browser-zoom";
import { injectMimicZoomContext } from "./context";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();

const context = injectMimicZoomContext();
const { scroller, content, contentStyle, fitting } = context;

useBrowserZoomCapture(context);
</script>

<template>
  <!-- Auto margins centre the mimic while it fits and still allow scrolling to every edge. -->
  <div
    :ref="(element) => (scroller = (element as HTMLElement | null) ?? undefined)"
    :class="cn('flex', fitting ? 'overflow-hidden' : 'overflow-auto', props.class)"
    tabindex="0"
    @dblclick.prevent.stop
  >
    <div
      :ref="(element) => (content = (element as HTMLElement | null) ?? undefined)"
      class="m-auto shrink-0 [&>svg]:block [&>svg]:size-full"
      :style="contentStyle"
    >
      <slot />
    </div>
  </div>
</template>
