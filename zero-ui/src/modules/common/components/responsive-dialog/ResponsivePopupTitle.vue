<script setup lang="ts">
import { useUIStore } from "@common/stores/ui";
import { computed, HTMLAttributes } from "vue";
import { storeToRefs } from "pinia";

const { breakpoints } = storeToRefs(useUIStore());

import DrawerTitle from "@components/drawer/DrawerTitle.vue";
import DialogTitle from "@components/dialog/DialogTitle.vue";

const wrapper = computed(() => (breakpoints.value.phone ? DrawerTitle : DialogTitle));
const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <component
    :is="wrapper"
    v-bind="props"
  >
    <slot />
  </component>
</template>
