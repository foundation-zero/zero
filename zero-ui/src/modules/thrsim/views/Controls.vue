<script setup lang="ts">
import { ModuleDefinition } from "@/modules/thrapp/types/thrs";

import ControlValuesControls from "@/modules/thrsim/components/ControlValuesControls.vue";
import { DEFINITIONS } from "@/modules/thrapp/lib/consts";
import { CONTROLS_PAGE_QUERIES } from "@/modules/thrapp/lib/queries.consts";
import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { storeToRefs } from "pinia";
import { computed, inject, Ref, watchEffect } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
const definition = computed<ModuleDefinition>(() => DEFINITIONS[currentDefinition.value]);

const { activeQuery } = storeToRefs(useThrsHistory());
watchEffect(() => (activeQuery.value = CONTROLS_PAGE_QUERIES[currentDefinition.value]));
</script>
<template>
  <header class="text-3xl capitalize">
    {{ t("thrs.views.controls.title") }}
  </header>

  <ControlValuesControls
    class="my-4 md:my-6"
    :module="currentDefinition"
    :definition="definition.controlValues"
  />
</template>
