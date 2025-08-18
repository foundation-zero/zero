<script setup lang="ts">
import { ValidationStatus } from "@/@types";
import { ExclamationTriangleIcon } from "@radix-icons/vue";
import { inject, Ref } from "vue";

defineProps<{ state?: ValidationStatus; title: string; selectable?: boolean }>();

const disabled = inject<Ref<boolean>>("disabled");
</script>

<template>
  <li
    class="border-primary/20 bg-primary/5 text-primary/85 dark:bg-primary/10 relative flex aspect-4/3 flex-col justify-between rounded border px-[0.625em] py-[0.3em] transition-all 2xl:aspect-16/10"
    :class="{
      'hover:bg-primary/15 hover:text-primary cursor-pointer': selectable && !disabled,
      'cursor-wait': disabled,
      [state ?? ValidationStatus.UNKNOWN]: true,
    }"
  >
    <div class="absolute top-8 right-0 bottom-0 left-0">
      <slot name="background" />
    </div>
    <span class="flex w-full items-center">
      <slot name="top-left">
        <span class="text-rlg overflow-hidden pr-1 text-ellipsis whitespace-nowrap">{{
          title
        }}</span>
      </slot>
      <span class="grow" />
      <slot name="top-right">
        <ExclamationTriangleIcon class="text-primary/90 h-[1.25em] w-[1.25em]" />
      </slot>
    </span>

    <span class="text-r5xl flex place-items-baseline justify-center font-bold">
      <slot name="center" />
    </span>

    <span class="flex min-h-3 w-full items-center">
      <slot name="bottom-left" />
      <span class="grow" />
      <slot name="bottom-right" />
    </span>
  </li>
</template>

<style lang="scss" scoped>
li {
  &.unknown,
  &.ok {
    --primary: oklch(0.3211 0 0);

    &:is(.dark *) {
      --primary: oklch(0.8452 0 0);
    }

    svg {
      display: none;
    }
  }

  &.warn {
    --primary: oklch(0.7176 0.1612 61.43);
  }
  &.fail {
    --primary: oklch(0.6356 0.2082 25.38);
  }
}
</style>
