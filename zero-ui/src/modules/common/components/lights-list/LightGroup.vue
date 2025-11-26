<script setup lang="ts">
import { LightGroup } from "@/modules/domestic/types";
import { List, ListRoot } from "@common/components/list";
import ListHeader from "@common/components/list/ListHeader.vue";
import LightGroupItem from "./LightGroupItem.vue";

defineProps<{ group: LightGroup }>();
</script>

<template>
  <ListRoot>
    <ListHeader>{{ group.name }}</ListHeader>
    <List>
      <LightGroupItem
        v-for="light in group.controls"
        :key="light.name!"
        :control="light"
        class="flex-col space-y-3 py-6"
      />
    </List>
  </ListRoot>
</template>
