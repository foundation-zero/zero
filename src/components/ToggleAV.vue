<script setup lang="ts">
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useDark } from "@vueuse/core";
import { Music } from "lucide-vue-next";
const isDark = useDark();
</script>

<template>
  <div class="flex items-center space-x-3 text-sm">
    <Label for="av-toggle">
      <Music
        class="inline"
        :size="18"
        stroke-width="2"
      />
    </Label>
    <Switch
      id="av-toggle"
      :checked="isDark"
      @update:checked="(val) => (isDark = val)"
    >
    </Switch>
  </div>
</template>
