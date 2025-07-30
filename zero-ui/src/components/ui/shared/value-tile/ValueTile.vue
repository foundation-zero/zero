<script setup lang="ts">
import { ValidationStatus } from "@/@types";
import { ExclamationTriangleIcon } from "@radix-icons/vue";
import { inject, Ref } from "vue";

defineProps<{ state?: ValidationStatus; title: string; selectable?: boolean }>();

const disabled = inject<Ref<boolean>>("disabled");
</script>

<template>
  <li
    class="relative flex aspect-[4/3] flex-col justify-between rounded-lg border border-primary/20 bg-primary/5 px-[0.625em] py-[0.3em] text-primary/85 transition-all dark:bg-primary/10 2xl:aspect-[16/10]"
    :class="{
      'cursor-pointer hover:bg-primary/15 hover:text-primary/100': selectable && !disabled,
      'cursor-wait': disabled,
      [state ?? ValidationStatus.UNKNOWN]: true,
    }"
  >
    <div class="absolute bottom-0 left-0 right-0 top-8">
      <slot name="background" />
    </div>
    <span class="flex w-full items-center">
      <slot name="top-left">
        <span class="overflow-hidden text-ellipsis whitespace-nowrap pr-1 text-rlg">{{
          title
        }}</span>
      </slot>
      <span class="grow" />
      <slot name="top-right">
        <ExclamationTriangleIcon class="h-[1.25em] w-[1.25em] text-primary/90" />
      </slot>
    </span>

    <span class="flex place-items-baseline justify-center text-r5xl font-bold">
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
    --primary: 0 0% 20%;

    &:is(.dark *) {
      --primary: 0 0% 80%;
    }

    svg {
      display: none;
    }
  }

  &.warn {
    --primary: 32.5 83.5% 50%;
  }
  &.fail {
    --primary: 0 84% 60%;
  }
}
</style>
