<script setup lang="ts">
import { ResponsivePopup } from "@/modules/common/components/responsive-dialog";
import { computed } from "vue";
import { createTooltipContext, provideTooltipContext } from ".";
import NoopTooltipProvider from "./NoopTooltipProvider.vue";

const tooltipContext = createTooltipContext();
provideTooltipContext(tooltipContext);

const { component, data, clear } = tooltipContext;

const isOpen = computed({
  get() {
    return data.value !== null;
  },
  set(value: boolean) {
    if (!value) {
      clear();
    }
  },
});
</script>

<template>
  <ResponsivePopup
    v-model:open="isOpen"
    class="bg-muted max-h-[90vh]! w-screen! max-w-150! px-0 pb-0 sm:w-[95vw]!"
  >
    <template #title>
      <h2 class="px-4 text-left text-3xl text-[2rem] font-semibold sm:px-6">
        {{ data?.tooltip?.title }}
      </h2>
    </template>
    <NoopTooltipProvider>
      <div class="max-md:px-4">
        <component
          :is="component"
          v-if="component"
          v-bind="data"
        />
      </div>
    </NoopTooltipProvider>
  </ResponsivePopup>

  <slot />
</template>
