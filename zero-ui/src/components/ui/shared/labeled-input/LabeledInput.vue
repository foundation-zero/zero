<script setup lang="ts">
import { useVModel } from "@vueuse/core";
import { HTMLAttributes, ref } from "vue";
import { Input } from "../../shadcn/input";

const props = defineProps<{
  title: string;
  defaultValue?: string | number;
  modelValue?: string | number;
  placeholder?: string;
  class?: HTMLAttributes["class"];
  invalid?: boolean;
}>();

const emits = defineEmits<{
  (e: "update:modelValue", payload: string | number): void;
}>();

const modelValue = useVModel(props, "modelValue", emits, {
  passive: true,
  defaultValue: props.defaultValue,
});

const hasFocus = ref(false);
</script>

<template>
  <div class="relative grid">
    <Input
      v-model="modelValue"
      class="h-10 pt-2 pb-0 text-sm transition-all placeholder:opacity-0 placeholder:transition-opacity placeholder:duration-250 focus-visible:placeholder:opacity-100"
      :invalid="invalid"
      :placeholder="placeholder"
      @focus="hasFocus = true"
      @blur="hasFocus = false"
    />

    <label
      class="absolute px-3 transition-all duration-150"
      :class="{
        'top-1/2 -translate-y-1/2 text-sm': !hasFocus && !modelValue,
        'text-2xs text-disabled-foreground top-0.75 translate-none': hasFocus || modelValue,
      }"
      >{{ props.title }}</label
    >
  </div>
</template>
