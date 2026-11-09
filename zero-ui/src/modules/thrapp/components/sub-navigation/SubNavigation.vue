<script setup lang="ts">
import { SubNavigationProps } from "@/modules/thrapp/components/navigation";
import { useAutomationStore } from "@/modules/thrapp/stores/automation";
import { computed, provide, toRefs } from "vue";
import ControlState from "./ControlState.vue";
import ModuleSelector from "./ModuleSelector.vue";
import SubNavigationModes from "./SubNavigationModes.vue";
import { getControlModule, getControlState } from "./sub-navigation.utils";

/** Context of the selected module: module selector, its modes and how it is controlled. */
const props = defineProps<SubNavigationProps>();

const { control } = toRefs(useAutomationStore());

// Sub-modules (e.g. the PVT biminis) are controlled through their module.
const controlModule = computed(() => props.activeModule && getControlModule(props.activeModule));
const controlState = computed(() => getControlState(control.value, controlModule.value));

provide("currentModule", controlModule);
</script>

<template>
  <div
    class="bg-background relative w-full border-b"
    :class="controlState === 'manual' ? 'border-warning border-b-2' : 'border-border-subtle'"
    data-testid="sub-navigation"
    :data-control-state="controlState"
  >
    <div
      v-if="controlState === 'manual'"
      class="bg-warning/8 pointer-events-none absolute inset-0"
    />
    <div
      class="relative flex flex-wrap items-center justify-between gap-x-6 gap-y-2.5 px-4 py-3 lg:flex-nowrap lg:px-6"
    >
      <ModuleSelector
        :modules="modules"
        :active-module="activeModule"
      />
      <div class="flex min-h-6 items-center lg:order-last">
        <ControlState :state="controlState" />
      </div>
      <SubNavigationModes
        :module="controlModule"
        class="basis-full lg:flex-1 lg:basis-auto"
      />
    </div>
  </div>
</template>
