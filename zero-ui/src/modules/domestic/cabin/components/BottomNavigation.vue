<script setup lang="ts">
import BottomTabs from "@/modules/common/components/navigation/BottomTabs.vue";
import { NavItem } from "@/modules/common/types";

const navItems: NavItem[] = [
  { title: "labels.airconditioning.short", to: "cabin:airconditioning" },
  { title: "labels.lights", to: "cabin:lights" },
  { title: "labels.blinds", to: "cabin:blinds" },
];
</script>

<template>
  <BottomTabs :items="navItems" />
</template>
