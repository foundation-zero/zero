<script lang="ts" setup>
import { Room } from "@/@types";
import Switch from "@/components/ui/shadcn/switch/Switch.vue";
import { toRef } from "vue";
import { useToggleableLights } from ".";

const props = defineProps<{
  rooms: Room[];
}>();

const { someLightsAreOn, toggle } = useToggleableLights(toRef(props, "rooms"));
</script>

<template>
  <Switch
    :checked="someLightsAreOn"
    class="scale-125 md:scale-150"
    @click="toggle"
  />
</template>
