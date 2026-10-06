<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  iconClass?: HTMLAttributes["class"];
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <svg
    :class="cn('size-6', props.class)"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g :class="cn('fill-brand', props.iconClass)">
      <path
        d="M17.1667 21.3333H8.83333V19.6666H17.1667V21.3333ZM11.3333 7.16663H14.6667V4.66663H16.3333V7.16663H19.6667C20.1269 7.16663 20.5 7.53973 20.5 7.99996V15.5C20.5 17.3409 19.0076 18.8333 17.1667 18.8333H8.83333C6.99238 18.8333 5.5 17.3409 5.5 15.5V7.99996C5.5 7.53973 5.8731 7.16663 6.33333 7.16663H9.66667V4.66663H11.3333V7.16663ZM7.16667 15.5C7.16667 16.4205 7.91286 17.1666 8.83333 17.1666H17.1667C18.0872 17.1666 18.8333 16.4205 18.8333 15.5V8.83329H7.16667V15.5Z"
      />
    </g>
  </svg>
</template>
