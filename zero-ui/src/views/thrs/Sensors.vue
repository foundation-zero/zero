<script setup lang="ts">
import ModuleSensors from "@/components/modules/hmi/ModuleSensors.vue";

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
    {{ t("views.thrs.hmi.sensors") }}
  </header>
  <ModuleSensors
    :module="currentDefinition"
    :sensors="definition.sensorValues"
    :query="QUERIES[currentDefinition].sensorValues"
    :client="client"
  />
</template>
