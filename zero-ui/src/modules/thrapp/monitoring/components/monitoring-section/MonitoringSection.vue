<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { RiArrowDownSLine } from "@remixicon/vue";
import { useLocalStorage } from "@vueuse/core";
import { type HTMLAttributes, ref, useId } from "vue";

/**
 * A heading that opens and closes the content under it. A section groups panels
 * in muted capitals, a group titles one panel.
 */
const props = withDefaults(
  defineProps<{
    title: string;
    /** Remembers per viewer whether a section is open. */
    storageKey: string;
    level?: "section" | "group";
    class?: HTMLAttributes["class"];
  }>(),
  { level: "section", class: undefined },
);

// Sections remember per viewer whether they are open; groups open on every visit.
const open =
  props.level === "section"
    ? useLocalStorage(`thrs-monitoring-open:${props.storageKey}`, true)
    : ref(true);
const contentId = useId();
</script>

<template>
  <section :class="cn('flex flex-col', props.level === 'section' ? 'gap-4' : 'gap-2', props.class)">
    <div
      :class="
        cn('flex items-center gap-4', props.level === 'section' && 'border-border border-b pb-2')
      "
    >
      <button
        type="button"
        class="text-foreground hover:text-foreground/80 flex w-fit items-center gap-1.5"
        :aria-expanded="open"
        :aria-controls="contentId"
        @click="open = !open"
      >
        <RiArrowDownSLine
          :class="cn('size-4 shrink-0 transition-transform', !open && '-rotate-90')"
          aria-hidden="true"
        />
        <h2
          v-if="props.level === 'section'"
          class="font-headers text-muted-foreground text-base leading-5 font-bold tracking-wider uppercase"
        >
          {{ props.title }}
        </h2>
        <h3
          v-else
          class="font-headers text-base leading-5 font-semibold"
        >
          {{ props.title }}
        </h3>
      </button>
      <slot name="actions" />
    </div>
    <div
      v-show="open"
      :id="contentId"
      :class="cn('flex flex-col', props.level === 'section' ? 'gap-8' : 'gap-3')"
    >
      <slot />
    </div>
  </section>
</template>
