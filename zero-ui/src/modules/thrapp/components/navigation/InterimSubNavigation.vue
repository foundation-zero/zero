<script setup lang="ts">
import ControlActions from "@/modules/thrapp/components/control-actions/ControlActions.vue";
import { ThrsModules } from "@/modules/thrapp/lib/consts";
import { SubNavigationProps } from "./navigation.types";
import ModuleTabs from "./ModuleTabs.vue";

/** Stop-gap sub navigation: the module tabs and the control state in one row. */
defineProps<SubNavigationProps>();
</script>

<template>
  <div
    class="border-border-subtle flex items-center gap-4 border-b px-4 py-1 md:px-6 md:py-2"
    data-testid="sub-navigation"
  >
    <div class="flex min-w-0 flex-1 overflow-x-auto">
      <ModuleTabs
        :modules="modules"
        :active-module="activeModule"
      />
    </div>
    <div class="flex shrink-0 items-center">
      <ControlActions
        v-if="activeModule"
        :active-module="activeModule as keyof ThrsModules"
      />
    </div>
  </div>
</template>
