<script setup lang="ts">
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useDark } from "@vueuse/core";

const isDark = useDark();
</script>

<template>
  <div class="flex items-center space-x-3 text-sm">
    <Label
      for="av-toggle"
      class="font-light"
    >
      A/V System
    </Label>
    <Switch
      id="av-toggle"
      :checked="isDark"
      @update:checked="(val) => (isDark = val)"
    >
    </Switch>
  </div>
</template>
