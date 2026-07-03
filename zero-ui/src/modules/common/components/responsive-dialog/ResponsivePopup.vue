<script setup lang="ts">
import { useUIStore } from "@common/stores/ui";
import { computed, HTMLAttributes, toRefs } from "vue";

const { breakpoints } = toRefs(useUIStore());

import dialog from "./ResponsivePopupDialog.vue";
import drawer from "./ResponsivePopupDrawer.vue";

const wrapper = computed(() => (breakpoints.value.phone ? drawer : dialog));
const open = defineModel<boolean>("open", { required: true, default: false });
const props = defineProps<{
  title?: string;
  description?: string;
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <component
    :is="wrapper"
    v-model:open="open"
    :title="title"
    :description="description"
    :class="props.class"
  >
    <template
      v-if="$slots['title']"
      #title
    >
      <slot name="title" />
    </template>
    <template #trigger>
      <slot name="trigger" />
    </template>
    <slot />
  </component>
</template>
