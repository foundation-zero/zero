<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useSimulationStore } from "@/modules/thrs/stores/simulation";
import { tScoped } from "@common/lib/utils";
import { useLocalStorage } from "@vueuse/core";
import { PauseIcon, Play, RedoDot, Settings } from "lucide-vue-next";
import { toRefs } from "vue";

const { pause, play, step } = useSimulationStore();
const { isRunning, isAvailable, isProcessing, isStepping } = toRefs(useSimulationStore());

const $t = tScoped("thrs.components.simulationActions");

const playbackRate = useLocalStorage("simulation:playbackRate", 1.0);

const toggle = async () => {
  if (isAvailable.value) {
    await play(playbackRate.value);
  } else if (isRunning.value) {
    await pause();
  }
};

const next = () => step(playbackRate.value);
</script>

<template>
  <div
    class="flex items-center gap-2"
    data-testid="thrs-actions"
  >
    <Popover>
      <PopoverTrigger>
        <Button
          variant="ghost"
          size="icon"
          :disabled="isRunning"
        >
          <Settings />
        </Button>
      </PopoverTrigger>
      <PopoverContent class="z-10">
        <header class="mb-3 text-lg font-semibold">{{ $t("title") }}</header>
        <hgroup>
          <header class="mb-1 text-sm">
            {{ $t("playbackRate") }}
          </header>
          <NumberField
            v-model="playbackRate"
            :disabled="isProcessing"
            :step="0.25"
            :min="0.25"
            :max="10"
          >
            <NumberFieldContent>
              <NumberFieldDecrement />
              <NumberFieldInput />
              <NumberFieldIncrement />
            </NumberFieldContent>
          </NumberField>
        </hgroup>
      </PopoverContent>
    </Popover>

    <Button
      :variant="isRunning ? 'default' : 'secondary'"
      :disabled="isProcessing || isStepping"
      size="icon"
      @click="toggle()"
    >
      <PauseIcon v-if="isRunning" />
      <Play v-else />
    </Button>

    <Button
      variant="ghost"
      size="icon"
      :disabled="isProcessing || isRunning"
      @click="next()"
    >
      <RedoDot />
    </Button>
  </div>
</template>
