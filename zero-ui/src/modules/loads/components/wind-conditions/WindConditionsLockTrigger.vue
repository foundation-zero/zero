<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { useTimeoutFn } from "@vueuse/core";
import { ArrowBigLeft } from "lucide-vue-next";
import { nextTick, ref } from "vue";

const isAnimating = ref(false);

const triggerAnimation = async () => {
  isAnimating.value = false;
  await nextTick();
  isAnimating.value = true;

  // Trigger the lock action after a short delay to allow the animation to start
  useTimeoutFn(() => emit("trigger"), 500);
};

const emit = defineEmits(["trigger"]);
</script>

<template>
  <Button
    variant="ghost"
    size="icon"
    class="lock-trigger"
    @click="triggerAnimation"
  >
    <span class="lock-trigger__icon">
      <ArrowBigLeft
        stroke-width="2"
        class="lock-trigger__icon-base"
      />
      <ArrowBigLeft
        stroke-width="2"
        class="lock-trigger__icon-fill"
        :class="{ 'is-animating': isAnimating }"
        @animationend="isAnimating = false"
      />
    </span>
  </Button>
</template>

<style scoped>
.lock-trigger__icon {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.lock-trigger__icon :deep(svg) {
  width: 1.1rem;
  height: 1.1rem;
}

.lock-trigger__icon-base {
  opacity: 0.45;
}

.lock-trigger__icon-fill {
  position: absolute;
  inset: 0;
  clip-path: inset(0 0 0 100%);
  opacity: 0;
  fill: var(--color-constructive);
  color: var(--color-constructive);
}

.lock-trigger__icon-fill.is-animating {
  animation: lock-trigger-fill 3s ease-out;
}

@keyframes lock-trigger-fill {
  0% {
    clip-path: inset(0 0 0 100%);
    opacity: 0;
  }
  15% {
    opacity: 1;
  }
  30% {
    clip-path: inset(0 0 0 0);
    opacity: 1;
  }
  100% {
    clip-path: inset(0 0 0 0);
    opacity: 0;
  }
}
</style>
