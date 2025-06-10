<script lang="ts" setup>
import { Room } from "@/@types";
import Switch from "@components/shadcn/switch/Switch.vue";
import { defineProps, toRef } from "vue";
import { useToggleableLights } from ".";

const props = defineProps<{
  rooms: Room[];
}>();

const { someLightsAreOn, toggle } = useToggleableLights(toRef(props, "rooms"));
</script>

<template>
  <Switch
    :checked="someLightsAreOn"
    @click="toggle"
  />
</template>
