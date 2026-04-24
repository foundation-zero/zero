<script setup lang="ts">
import { TopNavToolbar } from "@/modules/common/components/navigation";
import NavPills from "@/modules/common/components/navigation/NavPills.vue";
import { BREAKPOINTS } from "@/modules/common/stores/ui";
import { NavItem } from "@/modules/common/types";
import RoomSelector from "../../components/RoomSelector.vue";
import ToggleAV from "./ToggleAV.vue";

const navItems: NavItem[] = [
  { title: "labels.airConditioning.long", to: "cabin:air-conditioning" },
  { title: "labels.lights", to: "cabin:lights" },
  { title: "labels.blinds", to: "cabin:blinds" },
];
</script>

<template>
  <TopNavToolbar class="py-1">
    <template #right-content>
      <ToggleAV />
    </template>
    <template
      v-if="BREAKPOINTS.greaterOrEqual('sm').value"
      #center
    >
      <NavPills :items="navItems" />
    </template>
    <template #left-content>
      <RoomSelector />
    </template>
  </TopNavToolbar>
</template>
