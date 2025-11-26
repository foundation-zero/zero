<script lang="ts" setup>
import Switch from "@/components/ui/switch/Switch.vue";
import { Room } from "@/modules/domestic/types";
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
