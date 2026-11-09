import { useCountdown } from "@vueuse/core";
import { computed, ref } from "vue";
import { UNLOCK_COUNTDOWN_SECONDS } from "./manual-mode-toggle.consts";

/**
 * Password check plus countdown before switching a module to manual control: `confirm` starts
 * the countdown when the password matches, `unlock` runs when it ends unless `cancel` stops it.
 */
export function useManualModeUnlock(
  matchPassword: string | undefined,
  unlock: () => Promise<unknown> | void,
) {
  const password = ref("");
  const isValid = computed(() => !!matchPassword && password.value === matchPassword);

  const { start, stop, remaining, isActive } = useCountdown(UNLOCK_COUNTDOWN_SECONDS, {
    onComplete: unlock,
  });

  const confirm = () => {
    if (isValid.value && !isActive.value) {
      start();
    }
  };

  return { password, isValid, confirm, cancel: stop, remaining, isActive };
}
