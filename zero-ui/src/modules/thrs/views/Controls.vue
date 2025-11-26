<script setup lang="ts">
import ModuleControls from "@/modules/thrs/components/ModuleControls.vue";
import { ModuleDefinition } from "@/modules/thrs/types";

import { DEFINITIONS, QUERIES } from "@/modules/thrs/lib/consts";
import { useClientHandle } from "@urql/vue";
import { computed, inject, Ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const { client } = useClientHandle();
const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
const definition = computed<ModuleDefinition>(() => DEFINITIONS[currentDefinition.value]);
</script>
<template>
  <header class="mb-4 text-3xl capitalize">
    {{ t("views.thrs.hmi.controls") }}
  </header>

  <ModuleControls
    :module="currentDefinition"
    :controls="definition.controlValues"
    :query="QUERIES[currentDefinition].controlValues"
    :client="client"
  />
</template>
