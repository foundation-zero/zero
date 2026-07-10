<script setup lang="ts">
import { ResponsivePopup } from "@/modules/common/components/responsive-dialog";
import { computed } from "vue";
import { createTooltipContext, provideTooltipContext } from ".";
import { MimicComponentFieldsMap } from "../../mimics/modules";

const props = defineProps<{
  source: Partial<MimicComponentFieldsMap>;
}>();

const tooltipContext = createTooltipContext(props.source);
provideTooltipContext(tooltipContext);

const { component, dialog, data, clear, closeDialog } = tooltipContext;

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
    class="bg-background px-0 pb-0"
    :class="{ 'max-h-[90vh]! w-screen! max-w-150! sm:w-[95vw]!': !dialog }"
  >
    <template
      v-if="!dialog"
      #title
    >
      <h2 class="px-4 text-left text-3xl text-[2rem] font-semibold sm:px-6">
        {{ data?.tooltip?.title }}
      </h2>
    </template>

    <div class="max-md:px-4">
      <component
        :is="dialog"
        v-if="dialog"
        @close="closeDialog"
      />
      <component
        :is="component"
        v-else-if="component"
        v-bind="data"
      />
    </div>
  </ResponsivePopup>

  <slot />
</template>
