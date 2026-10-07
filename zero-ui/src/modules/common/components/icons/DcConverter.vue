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
    :class="cn('size-5', props.class)"
    viewBox="0 0 20 20"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g :class="cn('stroke-brand', props.iconClass)">
      <path
        d="M13.75 5H6.25C5.55964 5 5 5.55964 5 6.25V13.75C5 14.4404 5.55964 15 6.25 15H13.75C14.4404 15 15 14.4404 15 13.75V6.25C15 5.55964 14.4404 5 13.75 5Z"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M1.66667 10H5.00001"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M15 10H18.3333"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M13.4487 13.2854H9.83971"
        stroke-width="0.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M10.2689 6.73022H6.65991"
        stroke-width="0.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M10.673 12.0587H9.83964"
        stroke-width="0.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M14.5636 5.39404L5.45003 14.5682"
        stroke-width="0.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M7.49329 7.79138H6.65995"
        stroke-width="0.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M13.4487 12.0587H12.6154"
        stroke-width="0.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M10.2689 7.79138H9.43559"
        stroke-width="0.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </g>
  </svg>
</template>
