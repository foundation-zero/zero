<script setup lang="ts">
import BoilersModule from "@/modules/thrapp/mimics/modules/boilers/BoilersModule.vue";
import { DEFINITIONS } from "@/modules/thrs/lib/consts";
import { inject, Ref } from "vue";

const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
</script>
<template>
  <BoilersModule v-if="currentDefinition === 'boilers'" />
</template>
