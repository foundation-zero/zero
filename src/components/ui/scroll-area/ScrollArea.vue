<script setup lang="ts">
import { cn } from "@/lib/utils";
import {
  ScrollAreaCorner,
  ScrollAreaRoot,
  ScrollAreaViewport,
  type ScrollAreaRootProps,
} from "radix-vue";
import { computed, onMounted, type HTMLAttributes } from "vue";
import ScrollBar from "./ScrollBar.vue";

const props = defineProps<
  ScrollAreaRootProps & { class?: HTMLAttributes["class"]; scrollPosition?: number }
>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;

  return delegated;
});

const emit = defineEmits(["scrollY"]);

const onScroll = (event: Event) => emit("scrollY", (event.target as HTMLElement).scrollTop);

onMounted(() => {
  if (props.scrollPosition) {
    document.getElementById("scroll:rooms")?.scrollTo({ top: props.scrollPosition });
  }
});
</script>

<template>
  <ScrollAreaRoot
    v-bind="delegatedProps"
    :class="cn('relative overflow-hidden', props.class)"
  >
    <ScrollAreaViewport
      id="scroll:rooms"
      class="h-full w-full rounded-[inherit]"
      @scroll="onScroll"
    >
      <slot />
    </ScrollAreaViewport>
    <ScrollBar />
    <ScrollAreaCorner />
  </ScrollAreaRoot>
</template>
