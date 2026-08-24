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
import { useSimulationStore } from "@/modules/thrsim/stores/simulation";
import { tScoped } from "@common/lib/utils";
import { RiPauseLine, RiPlayLine, RiRestartLine, RiSettingsLine } from "@remixicon/vue";
import { useLocalStorage, watchDebounced } from "@vueuse/core";
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

watchDebounced(
  playbackRate,
  async (rate) => {
    if (isRunning.value) await play(rate);
  },
  { debounce: 300 },
);
</script>

<template>
  <div
    class="flex items-center gap-0.5"
    data-testid="thrs-actions"
  >
    <Popover>
      <PopoverTrigger>
        <Button
          variant="ghost"
          size="icon"
        >
          <RiSettingsLine />
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
      variant="ghost"
      :disabled="isProcessing || isStepping"
      size="icon"
      :class="{ 'text-brand': isRunning }"
      @click="toggle()"
    >
      <RiPauseLine v-if="isRunning" />
      <RiPlayLine v-else />
    </Button>

    <Button
      variant="ghost"
      size="icon"
      :disabled="isProcessing || isRunning"
      @click="next()"
    >
      <RiRestartLine />
    </Button>
  </div>
</template>
