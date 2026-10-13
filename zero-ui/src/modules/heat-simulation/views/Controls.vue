<script setup lang="ts">
import { ModuleDefinition } from "@/modules/heat-simulation/types";

import ControlValuesControls
  from "@/modules/heat-simulation/components/ControlValuesControls.vue";
import { DEFINITIONS } from "@/modules/heat-simulation/lib/consts";
import { computed, inject, Ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
const definition = computed<ModuleDefinition>(() => DEFINITIONS[currentDefinition.value]);
</script>
<template>
  <header class="text-3xl capitalize">
    {{ t("heatSimulation.views.controls.title") }}
  </header>

  <ControlValuesControls
    class="my-4 md:my-6"
    :module="currentDefinition"
    :definition="definition.controlValues"
  />
</template>
