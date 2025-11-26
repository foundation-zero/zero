<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { DotsVerticalIcon } from "@radix-icons/vue";
import { BellDotIcon, Search } from "lucide-vue-next";
</script>

<template>
  <ul
    class="flex"
    data-testid="thrs-actions"
  >
    <li>
      <Button
        size="sm"
        variant="ghost"
      >
        <Search class="size-4" />
      </Button>
    </li>
    <li>
      <Button
        size="sm"
        variant="ghost"
      >
        <BellDotIcon class="size-4" />
      </Button>
    </li>
    <li>
      <Button
        size="sm"
        variant="ghost"
      >
        <DotsVerticalIcon class="size-4" />
      </Button>
    </li>
  </ul>
</template>
