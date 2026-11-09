<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { useThrappNavigation } from "./navigation.utils";

const t = tScoped("thrapp.components.navigation");

const { tabs } = useThrappNavigation();
</script>

<template>
  <ul
    class="flex self-stretch"
    data-testid="thrapp-nav"
  >
    <li
      v-for="tab in tabs"
      :key="tab.name"
      class="flex"
    >
      <RouterLink
        :to="tab.to"
        :aria-current="tab.active ? 'page' : undefined"
        class="focus-visible:ring-brand -mb-px inline-flex items-center border-b px-4 text-base whitespace-nowrap uppercase transition-colors outline-none focus-visible:ring-2 focus-visible:ring-inset"
        :class="
          tab.active
            ? 'border-attention text-foreground'
            : 'text-muted-foreground hover:text-foreground border-transparent'
        "
      >
        {{ t(tab.label) }}
      </RouterLink>
    </li>
  </ul>
</template>
