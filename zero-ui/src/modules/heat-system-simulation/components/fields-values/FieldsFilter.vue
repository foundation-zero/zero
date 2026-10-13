<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { getContext } from ".";

const { series, selected } = getContext();
</script>

<template>
  <ToggleGroup
    v-model:model-value="selected"
    variant="outline"
    type="multiple"
    class="col-span-full flex-wrap"
  >
    <template
      v-for="[field, serie] in series"
      :key="field"
    >
      <ToggleGroupItem
        v-if="serie.length"
        :value="field"
        class="h-auto w-auto min-w-auto px-3 py-2 capitalize lg:px-4"
        :aria-label="`Toggle ${field}`"
      >
        <span class="text-sm lg:text-base!">{{ field }}</span>
        <Badge
          class="text-2xs py-0 max-lg:hidden lg:text-base"
          variant="secondary"
        >
          {{ serie.length }}
        </Badge>
      </ToggleGroupItem>
    </template>
  </ToggleGroup>
</template>
