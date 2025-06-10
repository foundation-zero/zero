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
      class="flex cursor-pointer justify-between pb-2 pl-3 pr-3 text-sm font-bold uppercase tracking-tight text-primary/75"
      :class="{ 'border-b border-primary/10': !isOpen }"
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
