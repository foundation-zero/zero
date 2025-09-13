<script setup lang="ts">
import { CaretDownIcon } from "@radix-icons/vue";

defineProps({
  title: {
    type: String,
    required: true,
  },
  collapsible: {
    type: Boolean,
    default: true,
  },
});
const isOpen = defineModel<boolean>("open", {
  type: Boolean,
  default: false,
});

const toggle = () => {
  isOpen.value = !isOpen.value;
};
</script>

<template>
  <section>
    <header
      class="text-muted-foreground flex cursor-pointer justify-between pr-3 pb-2 pl-3 text-sm font-bold tracking-wider uppercase"
      :class="{ 'border-primary/10 border-b': !isOpen }"
      @click="toggle"
    >
      <span>{{ title }}</span>
      <button v-if="collapsible">
        <CaretDownIcon
          stroke-width="2"
          class="h-5 w-5 transition-transform duration-200"
          :class="{ '-rotate-90': !isOpen }"
        />
      </button>
    </header>
    <p
      class="overflow-hidden transition-all duration-200"
      :class="{ 'max-h-0': !isOpen, 'max-h-[1000px]': isOpen }"
    >
      <slot />
    </p>
  </section>
</template>
