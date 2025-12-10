<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { useSimulationStore } from "@/modules/thrs/stores/simulation";
import { Bot, BotOff } from "lucide-vue-next";
import { computed, toRefs } from "vue";

const props = defineProps<{
  module: string;
}>();

const { control, isProcessing } = toRefs(useSimulationStore());
const { setAutomatedControl } = useSimulationStore();

const isAutomated = computed(() => control.value?.modules?.[props.module].automatic ?? false);
</script>

<template>
  <Button
    variant="ghost"
    size="icon"
    :disabled="isProcessing"
    @click="setAutomatedControl(props.module)(!isAutomated)"
  >
    <Bot v-if="isAutomated" />
    <BotOff v-else />
  </Button>
</template>
