<script setup lang="ts">
import type { SubNavigationProps } from "@/modules/thrapp/components/navigation";
import {
  getControlModule,
  ModuleSelector,
  SubNavigationModes,
} from "@/modules/thrapp/components/sub-navigation";
import { computed } from "vue";

/**
 * The module selector and its current modes, as on the other THRS pages, without
 * the control switch: monitoring only reads, it never switches control.
 */
const props = defineProps<SubNavigationProps>();

const controlModule = computed(() => props.activeModule && getControlModule(props.activeModule));
</script>

<template>
  <div
    class="bg-background border-border-subtle w-full border-b"
    data-testid="sub-navigation"
  >
    <div class="flex flex-wrap items-center gap-x-6 gap-y-2.5 px-4 py-3 lg:flex-nowrap lg:px-6">
      <ModuleSelector
        :modules="props.modules"
        :active-module="props.activeModule"
      />
      <SubNavigationModes
        :module="controlModule"
        class="basis-full lg:flex-1 lg:basis-auto"
      />
    </div>
  </div>
</template>
