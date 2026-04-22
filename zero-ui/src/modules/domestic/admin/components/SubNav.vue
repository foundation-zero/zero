<script setup lang="ts">
import { TopNavToolbar } from "@/modules/common/components/navigation";
import NavPills from "@/modules/common/components/navigation/NavPills.vue";
import { NavItem } from "@/modules/common/types";

const navItems: NavItem[] = [
  { title: "labels.control", to: "environment:control" },
  { title: "labels.temperature", to: "environment:temperature" },
  { title: "labels.humidity", to: "environment:humidity" },
  { title: "labels.ventilation", to: "environment:ventilation" },
  { title: "labels.lights", to: "environment:lights" },
];
</script>

<template>
  <TopNavToolbar class="py-1.5">
    <template #left-content>
      <NavPills :items="navItems" />
    </template>
  </TopNavToolbar>
</template>
