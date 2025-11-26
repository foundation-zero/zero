<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { ref } from "vue";

type NavItem = {
  value: string;
  label: string;
};

const items: NavItem[] = [
  { value: "overview", label: "Overview" },
  { value: "mizzen", label: "Mizzen (R1)" },
  { value: "main", label: "Main" },
  { value: "code0", label: "Code-0" },
  { value: "blade", label: "Blade" },
];

const [firstItem] = items;
const selectedItem = ref<string>(firstItem.value);
</script>

<template>
  <Tabs v-model="selectedItem">
    <TabsList
      as="nav"
      class="py-0"
    >
      <TabsTrigger
        v-for="item in items"
        :key="item.label"
        :value="item.label"
        class="h-16 text-base font-medium"
      >
        {{ item.label }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
