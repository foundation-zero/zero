<script setup lang="ts">
import { useUIStore } from "@/stores/ui";
import { computed, defineAsyncComponent, toRefs } from "vue";

const { breakpoints } = toRefs(useUIStore());

const drawer = defineAsyncComponent(() => import("./ResponsivePopupDrawer.vue"));
const dialog = defineAsyncComponent(() => import("./ResponsivePopupDialog.vue"));

const wrapper = computed(() => (breakpoints.value.phone ? drawer : dialog));
const open = defineModel<boolean>("open", { required: true });
defineProps<{ title: string; description: string }>();
</script>

<template>
  <component
    :is="wrapper"
    v-model:open="open"
    :title="title"
    :description="description"
  >
    <template #trigger>
      <slot name="trigger" />
    </template>
    <slot />
  </component>
</template>
