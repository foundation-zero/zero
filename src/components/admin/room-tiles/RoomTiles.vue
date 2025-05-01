<script setup lang="ts">
import { Room, ValidateFn, ValidationStatus } from "@/@types";
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { ExclamationTriangleIcon } from "@radix-icons/vue";
import { toRefs } from "vue";

const { validate } = defineProps<{ validate?: ValidateFn<Room> }>();

const { areas } = toRefs(useRoomStore());
const { showSideNav } = toRefs(useUIStore());
</script>

<template>
  <section
    v-for="area in areas"
    :key="area.name"
    class="pb-8 text-[0.8rem] md:pb-12 md:text-[0.9rem] lg:text-[0.95rem] xl:text-[1.2rem] portrait:lg:text-[1rem]"
  >
    <header
      class="border-b pb-2 text-rxl font-bold uppercase tracking-tight text-primary/75 dark:text-primary/65 md:pb-4"
    >
      {{ area.name }}
    </header>
    <ul
      class="mt-4 grid grid-cols-2 gap-4 text-rbase transition-all md:mt-6 md:gap-6"
      :class="{
        'md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4': !showSideNav,
        'md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4': showSideNav,
      }"
    >
      <li
        v-for="room in area.rooms"
        :key="room.id"
        :class="[validate?.(room) ?? ValidationStatus.UNKNOWN]"
        class="flex aspect-[16/10] flex-col justify-between rounded-lg border border-primary/20 bg-primary/5 px-[0.625em] py-[0.3em] text-primary/85 dark:bg-primary/10"
      >
        <span class="flex w-full items-center">
          <slot
            name="top-left"
            v-bind="{ room }"
          >
            <span class="overflow-hidden text-ellipsis whitespace-nowrap pr-1 text-rlg">{{
              room.name
            }}</span>
          </slot>
          <span class="grow" />
          <slot
            name="top-right"
            v-bind="{ room }"
          >
            <ExclamationTriangleIcon class="h-[1.25em] w-[1.25em] text-primary/90" />
          </slot>
        </span>

        <span class="flex place-items-baseline justify-center text-r5xl font-bold">
          <slot
            name="center"
            v-bind="{ room }"
          />
        </span>

        <span class="flex min-h-3 w-full items-center">
          <slot
            name="bottom-left"
            v-bind="{ room }"
          />
          <span class="grow" />
          <slot
            name="bottom-right"
            v-bind="{ room }"
          />
        </span>
      </li>
    </ul>
  </section>
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
