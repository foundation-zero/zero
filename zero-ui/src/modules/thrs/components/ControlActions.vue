<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { useSimulationStore } from "@/modules/thrs/stores/simulation";
import { Bot, BotOff } from "lucide-vue-next";
import { computed, toRefs } from "vue";

const { control, isProcessing } = toRefs(useSimulationStore());
const { setAutomatedControl } = useSimulationStore();

const isAutomated = computed(() => control.value?.control.automatic ?? false);
</script>

<template>
  <Button
    :variant="isAutomated ? 'default' : 'secondary'"
    size="icon"
    :disabled="isProcessing"
    @click="setAutomatedControl(!isAutomated)"
  >
    <Bot v-if="isAutomated" />
    <BotOff v-else />
  </Button>
</template>
