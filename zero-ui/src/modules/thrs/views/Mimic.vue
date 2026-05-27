<script setup lang="ts">
import Label from "@/components/ui/label/Label.vue";
import { Switch } from "@/components/ui/switch";
import BoilersModule from "@/modules/thrapp/mimics/modules/boilers/BoilersModule.vue";
import { GraphQLProvider, MockProvider } from "@/modules/thrapp/mimics/providers";
import { DEFINITIONS } from "@/modules/thrs/lib/consts";
import { computed, inject, Ref, ref } from "vue";

const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;

const demoMode = ref(false);
const provider = computed(() => (demoMode.value ? MockProvider : GraphQLProvider));
</script>
<template>
  <div class="flex items-center gap-3">
    <Switch v-model="demoMode" />
    <Label> Demo Mode </Label>
  </div>
  <component
    :is="provider"
    v-if="currentDefinition === 'boilers'"
    module="boilers"
  >
    <BoilersModule />
  </component>
</template>
