<script setup lang="ts">
import { LightingGroups } from "@/gql/graphql";
import { toRefs } from "vue";
import { List, ListRoot } from "../list";
import ListHeader from "../list/ListHeader.vue";
import LightGroupItem from "./LightGroupItem.vue";

const props = defineProps<{ name: string; lights: LightingGroups[] }>();
const { lights, name } = toRefs(props);
</script>

<template>
  <ListRoot>
    <ListHeader>{{ name }}</ListHeader>
    <List>
      <LightGroupItem
        v-for="light in lights"
        :key="light.name!"
        v-model:level="light.level"
        :name="light.name!"
        class="flex-col space-y-3 py-6"
      />
    </List>
  </ListRoot>
</template>
