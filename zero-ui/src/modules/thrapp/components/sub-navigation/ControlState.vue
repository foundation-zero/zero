<script setup lang="ts">
import { Popover, PopoverAnchor, PopoverContent } from "@/components/ui/popover";
import { Switch } from "@/components/ui/switch";
import { tScoped } from "@/modules/common/lib/utils";
import AdvisoryModeTooltip from "@/modules/thrapp/components/control-actions/AdvisoryModeTooltip.vue";
import { ManualModeToggleDialog } from "@/modules/thrapp/components/manual-mode-toggle";
import { useAutomaticMode } from "@/modules/thrapp/state";
import { useAutomationStore } from "@/modules/thrapp/stores/automation";
import { ENV } from "@/settings";
import { RiLockLine } from "@remixicon/vue";
import { ref, toRefs, useId, useTemplateRef } from "vue";
import { ControlState } from "./sub-navigation.types";

defineProps<{ state?: ControlState }>();

const t = tScoped("thrapp.components.controlState");

const { isProcessing } = toRefs(useAutomationStore());
const isAutomatic = useAutomaticMode();

const requiresPassword = !!ENV.VITE_MANUAL_MODE_PWD;
const isUnlocking = ref(false);

const toggle = () => {
  if (isAutomatic.value && requiresPassword) {
    isUnlocking.value = true;
  } else {
    isAutomatic.value = !isAutomatic.value;
  }
};

const switchId = useId();
const toggleSwitch = useTemplateRef<{ $el: HTMLElement }>("toggleSwitch");

// The popover is anchored to the toggle instead of opened by it, so focus is returned by hand.
const returnFocus = (event: Event) => {
  event.preventDefault();
  toggleSwitch.value?.$el.focus();
};
</script>

<template>
  <AdvisoryModeTooltip
    v-if="state === 'advisoryDisabled'"
    class="text-muted-foreground text-base leading-4 font-medium"
  />

  <Popover
    v-else-if="state"
    v-model:open="isUnlocking"
  >
    <PopoverAnchor class="flex items-center gap-2">
      <label
        :for="switchId"
        class="cursor-pointer text-base leading-4 font-medium whitespace-nowrap"
        :class="{ 'text-warning': state === 'manual' }"
      >
        {{ state === "automatic" ? t("automaticControl") : t("manualControl") }}
      </label>
      <Switch
        :id="switchId"
        ref="toggleSwitch"
        :model-value="state === 'automatic' || isUnlocking"
        :disabled="isProcessing"
        class="focus-visible:ring-brand data-[state=checked]:bg-brand-muted data-[state=unchecked]:border-warning data-[state=unchecked]:bg-neutral-grey-1000 relative h-6 w-12 cursor-pointer focus-visible:ring-2"
        thumb-class="size-[22px] data-[state=checked]:bg-neutral-grey-600 data-[state=unchecked]:bg-warning data-[state=checked]:translate-x-6 data-[state=unchecked]:translate-x-0"
        @update:model-value="toggle"
      >
        <RiLockLine
          v-if="state === 'automatic'"
          class="text-brand-dull absolute left-2 size-4"
        />
      </Switch>
    </PopoverAnchor>

    <PopoverContent
      align="end"
      :side-offset="12"
      class="bg-background text-foreground w-auto rounded-2xl border-0 px-6 py-10 shadow-[0_0_4px_rgba(0,0,0,0.25)]"
      @close-auto-focus="returnFocus"
    >
      <ManualModeToggleDialog
        class="max-md:px-0"
        @close="isUnlocking = false"
      />
    </PopoverContent>
  </Popover>
</template>
