<script setup lang="ts">
import ModuleControls from "@/components/modules/hmi/ModuleControls.vue";

import { DEFINITIONS, QUERIES } from "@/lib/consts";
import { useClientHandle } from "@urql/vue";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const { client } = useClientHandle();
const currentDefinition = ref<keyof typeof DEFINITIONS>("thrusters");
const definition = computed(() => DEFINITIONS[currentDefinition.value]);
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
