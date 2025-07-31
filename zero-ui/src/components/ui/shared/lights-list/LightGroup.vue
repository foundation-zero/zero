<script setup lang="ts">
import { LightingControl } from "@/@types";
import { List, ListRoot } from "@/components/ui/shared/list";
import ListHeader from "@/components/ui/shared/list/ListHeader.vue";
import LightGroupItem from "./LightGroupItem.vue";

defineProps<{ name: string; lights: LightingControl[] }>();

const emit = defineEmits<{
  "update:level": [string, number];
}>();
</script>

<template>
  <ListRoot>
    <ListHeader>{{ name }}</ListHeader>
    <List>
      <LightGroupItem
        v-for="light in lights"
        :key="light.name!"
        :light="light"
        class="flex-col space-y-3 py-6"
        @update:level="emit('update:level', light.id, $event)"
      />
    </List>
  </ListRoot>
</template>
