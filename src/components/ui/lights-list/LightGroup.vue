<script setup lang="ts">
import { LightingGroups } from "@/gql/graphql";
import { List, ListRoot } from "../list";
import ListHeader from "../list/ListHeader.vue";
import LightGroupItem from "./LightGroupItem.vue";

defineProps<{ name: string; lights: LightingGroups[]; disabled?: boolean }>();

const emit = defineEmits(["update:level"]);

const updateLevel = (level: number, group: LightingGroups) => {
  group.level = level;
  emit("update:level", group);
};
</script>

<template>
  <ListRoot>
    <ListHeader>{{ name }}</ListHeader>
    <List>
      <LightGroupItem
        v-for="light in lights"
        :key="light.name!"
        :disabled="disabled"
        :level="light.level"
        :name="light.name!"
        class="flex-col space-y-3 py-6"
        @update:level="updateLevel($event, light)"
      />
    </List>
  </ListRoot>
</template>
